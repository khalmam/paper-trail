CSS = """
:root{color-scheme:light;--ink:#1d2433;--mute:#5b6577;--line:#d9dee7;--ok:#1f7a4d;--bad:#b3261e;--warn:#8a5a00;--bg:#f6f7f9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.2rem;margin:0 0 8px}h3{font-size:.95rem;margin:16px 0 6px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}
.sub{color:var(--mute);margin:0 0 16px}
.banner{border-radius:8px;padding:12px 14px;margin:12px 0;border:1px solid var(--line);background:#fff}
.banner.ok{border-color:var(--ok)}.banner.bad{border-color:var(--bad);background:#fdecea}
.banner b{display:block}.hash{font:12px/1.4 ui-monospace,Menlo,monospace;word-break:break-all;color:var(--mute)}
.notice{font-size:.9rem;color:var(--mute);border-left:3px solid var(--line);padding-left:10px;margin:12px 0}
section.issue{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;margin:16px 0}
.tag{display:inline-block;border-radius:999px;padding:1px 10px;font-size:.8rem;border:1px solid var(--line);margin-left:6px;vertical-align:middle}
.tag.open{border-color:var(--warn);color:var(--warn)}.tag.resolved{border-color:var(--ok);color:var(--ok)}.tag.late{border-color:var(--bad);color:var(--bad)}
table.facts{border-collapse:collapse;width:100%}table.facts th{text-align:left;width:34%;color:var(--mute);font-weight:500;padding:4px 8px 4px 0;vertical-align:top}table.facts td{padding:4px 0}
.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden;margin:4px 0}.bar i{display:block;height:100%;background:var(--ok)}
ul.flags{margin:6px 0;padding-left:20px}ul.flags li{margin:2px 0}
ol.timeline{list-style:none;margin:0;padding:0}ol.timeline li{border-top:1px solid var(--line);padding:6px 0}ol.timeline li:first-child{border-top:0}
.seq{font:12px ui-monospace,Menlo,monospace;color:var(--mute);margin-right:6px}.meta{color:var(--mute);font-size:.85rem}.fix{color:var(--warn);font-size:.8rem;margin-left:6px}
footer{color:var(--mute);font-size:.85rem;margin-top:24px}
@media print{body{background:#fff}main{padding:0}section.issue{break-inside:avoid;border-color:#999}.banner{break-inside:avoid}}
"""
