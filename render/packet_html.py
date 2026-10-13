"""Turns an evidence packet's data dictionary into one self-contained HTML page. Pure Python."""
import html

from .style import CSS


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def _banner(data: dict) -> str:
    i, head = data["integrity"], data.get("head_hash")
    if i["ok"]:
        top = f'<div class="banner ok"><b>Record check passed</b>All {esc(data["entry_count"])} entries are intact.'
    else:
        top = (f'<div class="banner bad"><b>Warning: this record failed its check</b>{esc(i["reason"])} '
               f'{esc(i["verified"])} earlier entries are intact. Treat what follows with care.')
    code = (f'<div class="hash">Newest entry code: {esc(head)}<br>Keep a copy of this code somewhere else. '
            f'Comparing it later shows whether earlier history was rewritten.</div>') if head else ""
    return top + code + "</div>"


def _when(days) -> str:
    if days is None:
        return "no deadline set"
    return "due today" if days == 0 else (f"{-days} day{'s' if days != -1 else ''} past" if days < 0
                                          else f"in {days} day{'s' if days != 1 else ''}")


def _facts(s: dict) -> str:
    deadline = "not set" if not s["deadline_on"] else f'{esc(s["deadline_on"])} ({esc(_when(s["days_until_deadline"]))}) {esc(s["deadline_what"])}'
    contact = "none recorded" if not s["contacts"] else (
        f'{s["contacts"]} recorded, latest {esc(s["last_contact_on"])} by {esc(str(s["last_contact_method"]).replace("_", " "))}')
    rows = [("Happened", esc(s["logged_on"])), ("Landlord told", contact), ("Deadline", deadline),
            ("Updates", esc(s["updates"])), ("Photos noted", esc(s["photo_refs"])),
            ("Witnesses named", esc(s["witnesses"])), ("Letters sent", esc(s["letters_sent"]))]
    return '<table class="facts">' + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</table>"


def _timeline(items: list[dict]) -> str:
    lines = []
    for it in items:
        fix = '<span class="fix">(corrected)</span>' if it["corrected"] else ""
        lines.append(f'<li><span class="seq">#{esc(it["seq"])}</span>{esc(it["text"])}{fix}'
                     f'<div class="meta">recorded {esc(it["at"][:10])} by {esc(it["author"])}</div></li>')
    return '<ol class="timeline">' + "".join(lines) + "</ol>"


def _issue(item: dict) -> str:
    s, c = item["summary"], item["completeness"]
    late = ' <span class="tag late">overdue</span>' if s["overdue"] else ""
    head = f'<h2>{esc(s["room"]).title()} {esc(s["category"])}<span class="tag {esc(s["status"])}">{esc(s["status"])}</span>{late}</h2>'
    rec = item["recurrence"]
    repeat = (f'<p>Reported {esc(rec["count"])} times in the last {esc(rec["window_days"])} days '
              f'({esc(rec["first_on"])} to {esc(rec["latest_on"])}).</p>') if rec else ""
    missing = ", ".join(m.replace("_", " ") for m in c["missing"])
    done = (f'<div class="bar"><i style="width:{int(c["percent"])}%"></i></div>'
            f'Evidence completeness: {esc(c["percent"])}%' + (f' (missing: {esc(missing)})' if missing else ""))
    flags = ""
    if item["conflicts"]:
        flags = "<h3>Where records differ</h3><ul class=\"flags\">" + "".join(
            f'<li>{esc(f["message"])}</li>' for f in item["conflicts"]) + "</ul>"
    return (f'<section class="issue">{head}<p>{esc(s["description"])}</p>{repeat}{_facts(s)}'
            f'<h3>Completeness</h3>{done}{flags}<h3>Suggested next step</h3><p>{esc(item["next_step"]["message"])}</p>'
            f'<h3>History</h3>{_timeline(item["timeline"]["items"])}</section>')


def render_packet(data: dict, title: str = "Evidence packet") -> str:
    body = "".join(_issue(i) for i in data["issues"]) or "<p>Nothing has been recorded yet.</p>"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
            f'<style>{CSS}</style></head><body><main><h1>{esc(title)}</h1>'
            f'<p class="sub">Prepared {esc(data["generated_on"])}. Demo data only.</p>'
            f'{_banner(data)}<p class="notice">{esc(data["notice"])}</p>{body}'
            f'<footer>Made with Paper Trail. This page is a prompt to review the record, not a verdict.</footer>'
            f'</main></body></html>')
