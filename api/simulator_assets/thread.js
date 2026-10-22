(function(){
var KIND={issue_logged:['Problem reported','#d9453d'],update:['Update','#8e8e93'],landlord_contact:['Landlord contacted','#0a84ff'],deadline_set:['Deadline set','#ff9f0a'],letter_sent:['Letter sent','#8e5cf7'],resolved:['Marked fixed','#30a46c'],correction:['Correction','#d6409f']};
var tokEl=document.getElementById('tok');
function mk(tag,cls,text){var n=document.createElement(tag);if(cls){n.className=cls}if(text!==undefined){n.textContent=text}return n}
var panel=mk('aside');panel.id='pt-panel';panel.setAttribute('aria-label','Sealed record');
panel.appendChild(mk('h2','','Sealed record'));
panel.appendChild(mk('p','pt-sub','Live from the MCP server. Each entry is locked to the one before it.'));
var badge=mk('div');badge.id='pt-badge';badge.setAttribute('role','status');
var bdot=mk('span','pt-dot');var btxt=mk('span','','Checking the record');
badge.appendChild(bdot);badge.appendChild(btxt);panel.appendChild(badge);
var vb=mk('button','pt-verify','Verify now');vb.type='button';panel.appendChild(vb);
var empty=mk('p','pt-empty','');panel.appendChild(empty);
var thread=mk('div','pt-thread');panel.appendChild(thread);
document.body.appendChild(panel);
var rows={},count=0,wasOk=null;
function row(e){
  var k=KIND[e.kind]||[e.kind.split('_').join(' '),'#8e8e93'];
  var r=mk('div','pt-row');r.style.setProperty('--dot',k[1]);r.dataset.hash=e.hash;
  r.appendChild(mk('span','pt-glow'));r.appendChild(mk('span','pt-line'));r.appendChild(mk('span','pt-node'));
  var b=mk('div','pt-body');var t=mk('div','pt-top');
  t.appendChild(mk('span','pt-kind',k[0]));t.appendChild(mk('span','pt-by',e.author+', '+e.date));b.appendChild(t);
  if(e.summary){b.appendChild(mk('div','pt-sum',e.summary))}
  b.appendChild(mk('div','pt-hash',e.seq===1?('seal '+e.hash+', first entry'):('seal '+e.hash+', follows '+e.prev_hash)));
  r.appendChild(b);return r;
}
function reset(){thread.textContent='';rows={};count=0}
function render(d){
  var i=d.integrity,es=d.entries;
  var stale=es.length<count;
  es.forEach(function(e){if(rows[e.seq]&&rows[e.seq].dataset.hash!==e.hash){stale=true}});
  var firstPaint=count===0||stale;
  if(stale){reset()}
  es.forEach(function(e,idx){
    if(rows[e.seq]){return}
    var r=row(e);rows[e.seq]=r;thread.appendChild(r);
    if(firstPaint){r.style.transitionDelay=(Math.min(idx,8)*40)+'ms'}
    else{r.classList.add('pt-fresh');setTimeout(function(){r.classList.remove('pt-fresh')},900)}
    requestAnimationFrame(function(){requestAnimationFrame(function(){
      r.classList.add('in');
      setTimeout(function(){r.style.transitionDelay=''},600);
    })});
  });
  es.forEach(function(e,idx){
    var r=rows[e.seq];if(!r){return}
    r.classList.toggle('pt-tail',idx===es.length-1);
    r.classList.toggle('pt-bad',!i.ok&&e.seq===i.bad_seq);
    r.classList.toggle('pt-unv',!i.ok&&e.seq>i.bad_seq);
    r.classList.toggle('pt-brk',!i.ok&&e.seq===i.bad_seq-1);
  });
  badge.classList.toggle('bad',!i.ok);
  btxt.textContent=i.ok?('Record intact. '+i.verified+' entries verified.'):(i.reason||('Entry '+i.bad_seq+' was altered.'));
  empty.textContent=es.length?'':'Nothing recorded yet. Report a problem and it appears here, sealed.';
  if(es.length!==count||wasOk!==i.ok){badge.style.transform='scale(1.02)';setTimeout(function(){badge.style.transform=''},160)}
  count=es.length;wasOk=i.ok;
}
function refresh(){
  if(!tokEl.value){btxt.textContent='Add an access token to see the record.';return}
  fetch('/api/ledger',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:tokEl.value})})
   .then(function(r){return r.ok?r.json():null})
   .then(function(d){if(d){render(d)}else{btxt.textContent='Could not load the record. Try Verify now.'}})
   .catch(function(){btxt.textContent='Could not reach the server. Try Verify now.'});
}
vb.onclick=refresh;
var of=window.fetch;
window.fetch=function(u){var p=of.apply(this,arguments);
  if(String(u).indexOf('/api/chat')>-1){p.then(function(){setTimeout(refresh,300)}).catch(function(){})}
  return p};
tokEl.addEventListener('input',refresh);
setTimeout(refresh,1200);setTimeout(refresh,3000);
})();
