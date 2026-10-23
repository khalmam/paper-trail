"""The simulator page: one self-contained HTML string. Typing stands in for speech."""
from django.http import HttpResponse

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper Trail simulator</title>
<style>
:root{color-scheme:light dark;--bg:#f6f7f9;--card:#fff;--ink:#1d2433;--mute:#5b6577;--line:#d9dee7;--me:#dbe8ff;--accent:#2457c5}
@media (prefers-color-scheme:dark){:root{--bg:#14171d;--card:#1d222b;--ink:#e8ecf3;--mute:#9aa4b5;--line:#313846;--me:#26385f;--accent:#7aa2ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:720px;margin:0 auto;padding:20px 16px 32px}h1{font-size:1.4rem;margin:0}
.sim{color:var(--mute);font-size:.9rem;margin:4px 0 14px;border-left:3px solid var(--accent);padding-left:10px}
label{display:block;font-size:.85rem;color:var(--mute);margin-bottom:10px}
input{width:100%;padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font:inherit}
#log{min-height:240px;display:flex;flex-direction:column;gap:10px;margin:12px 0}
.m{max-width:88%;padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:var(--card)}
.m p{margin:0;white-space:pre-wrap}.me{align-self:flex-end;background:var(--me)}
details{margin-top:8px;font-size:.8rem;color:var(--mute)}pre{overflow-x:auto;max-height:260px;font-size:.75rem}
#f{display:flex;gap:8px}button{padding:10px 16px;border:0;border-radius:8px;background:var(--accent);color:#fff;font:inherit;cursor:pointer}
.m.wait{color:var(--mute);font-style:italic}.confirm{display:flex;gap:8px;margin-top:10px}.confirm .no{background:transparent;color:var(--accent);border:1px solid var(--line)}.mic.on{background:#b3261e}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}.chips button{background:transparent;color:var(--accent);border:1px solid var(--line);padding:4px 10px;font-size:.85rem}
</style>
<style id="skin">
/*SKIN_CSS*/</style></head><body><main>
<h1>Paper Trail</h1>
<p class="pt-tag">Say it once. Prove it forever.</p>
<p class="sim">Simulated voice assistant. Typing stands in for speech. Demo data only. Not legal advice. Every message goes through the real MCP server.</p>
<p class="sim" id="demo-note" hidden>Demo access is filled in for you. This is a shared demo household with fake data.</p><label>Access token (from the seed output or the submission notes)
<input id="tok" type="password" autocomplete="off" placeholder="paste a demo token"></label>
<div class="chips" id="chips">
<button type="button">What's open?</button>
<button type="button">There is a leak in the kitchen sink</button>
<button type="button">Draft a letter</button>
<button type="button">I sent the letter</button>
<button type="button">Give me the packet</button>
<button type="button">Is my record intact?</button>
</div>
<div id="log" aria-live="polite"></div>
<form id="f"><input id="msg" autocomplete="off" placeholder="Tell me what's wrong, or ask what's open"><button>Send</button><button type="button" id="mic" class="mic" hidden>Mic</button></form>
<label><input type="checkbox" id="say" checked style="width:auto"> Speak replies aloud</label>
</main>
<script>
const log=document.getElementById('log'),tok=document.getElementById('tok'),msg=document.getElementById('msg');
let pending=null;
let hist=[];
function add(cls,text,extra){
  const d=document.createElement('div');d.className='m '+cls;
  const p=document.createElement('p');p.textContent=text;d.appendChild(p);
  if(extra)d.appendChild(extra);
  log.appendChild(d);d.scrollIntoView({block:'end'});
  return d;
}
async function send(text){
  if(!text)return;
  if(!tok.value.trim()){add('bot','Paste an access token first.');return}
  add('me',text);
  const wait=add('bot','Checking your record...');wait.classList.add('wait');
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text,token:tok.value.trim(),pending:pending,history:hist.slice(-8)})});
    const b=await r.json();
    if(r.status===422){add('bot','That request was missing something.');return}
    pending=b.pending||null;
    hist.push({role:'user',text:text},{role:'assistant',text:String(b.speech||'')});
    hist=hist.slice(-8);
    let extra=null;
    if(b.data){
      const det=document.createElement('details'),s=document.createElement('summary'),pre=document.createElement('pre');
      s.textContent='Details ('+b.tool+')';pre.textContent=JSON.stringify(b.data,null,2);
      det.appendChild(s);det.appendChild(pre);extra=det;
    }
    if(b.pending&&b.pending.confirm){
      const box=document.createElement('div');box.className='confirm';
      const yes=document.createElement('button');yes.type='button';yes.textContent='Yes, log it';
      const no=document.createElement('button');no.type='button';no.className='no';no.textContent='No, change it';
      const done=function(w){yes.disabled=true;no.disabled=true;send(w)};
      yes.onclick=function(){done('yes')};no.onclick=function(){done('no')};
      box.appendChild(yes);box.appendChild(no);
      if(extra){extra.appendChild(box)}else{extra=box}
    }
    add('bot',b.speech||'Done.',extra);speak(b.speech||'Done.');if(b.tool==='evidence_packet')showPacket();if(b.tool==='draft_letter'&&b.data)showLetter(b.data);
  }catch(e){add('bot','Could not reach the server.')}finally{wait.remove()}
}
function showLetter(l){
  const pre=document.createElement('pre');pre.style.whiteSpace='pre-wrap';
  pre.textContent=l.subject+'\\n\\n'+l.body+'\\n\\n'+l.note;
  const b=document.createElement('button');b.type='button';b.textContent='Copy letter';
  b.onclick=function(){navigator.clipboard.writeText(l.subject+'\\n\\n'+l.body)};
  const wrap=document.createElement('div');wrap.appendChild(pre);wrap.appendChild(b);
  add('bot','Here is your draft.',wrap);
}
let packetHtml=null;
async function showPacket(){
  try{
    const r=await fetch('/api/packet',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({token:tok.value.trim()})});
    if(!r.ok){add('bot','I could not build the packet.');return}
    packetHtml=await r.text();
    const f=document.createElement('iframe');
    f.setAttribute('sandbox','');
    f.style.cssText='width:100%;height:480px;border:1px solid var(--line);border-radius:8px;background:#fff';
    f.srcdoc=packetHtml;
    const b=document.createElement('button');b.type='button';b.textContent='Open printable page';
    b.onclick=function(){window.open(URL.createObjectURL(new Blob([packetHtml],{type:'text/html'})),'_blank')};
    const wrap=document.createElement('div');wrap.appendChild(f);wrap.appendChild(b);
    add('bot','Here is your packet.',wrap);
  }catch(e){add('bot','Could not reach the server.')}
}
document.getElementById('f').addEventListener('submit',function(e){
  e.preventDefault();const t=msg.value.trim();msg.value='';send(t);
});
document.getElementById('chips').addEventListener('click',function(e){
  if(e.target.tagName==='BUTTON')send(e.target.textContent);
});

const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const mic=document.getElementById('mic'),say=document.getElementById('say');
function speak(t){
  if(!say.checked||!window.speechSynthesis)return;
  speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(t));
}
if(SR){
  mic.hidden=false;
  const rec=new SR();rec.lang='en-US';rec.interimResults=false;
  rec.onresult=function(e){send(e.results[0][0].transcript)};
  rec.onend=rec.onerror=function(){mic.classList.remove('on')};
  mic.onclick=function(){
    if(window.speechSynthesis)speechSynthesis.cancel();
    try{mic.classList.add('on');rec.start()}catch(e){mic.classList.remove('on')}
  };
}
fetch('/api/demo-token').then(function(r){return r.ok?r.json():null}).then(function(b){
  if(b&&b.token){tok.value=b.token;document.getElementById('demo-note').hidden=false}
}).catch(function(){});
/*THREAD_JS*/

</script></body></html>"""


def simulator_page(_request):
    return HttpResponse(PAGE, content_type="text/html; charset=utf-8")

from pathlib import Path as _Path

_ASSETS = _Path(__file__).parent / "simulator_assets"
PAGE = (PAGE.replace("/*SKIN_CSS*/", (_ASSETS / "skin.css").read_text())
        .replace("/*THREAD_JS*/", (_ASSETS / "thread.js").read_text()))
