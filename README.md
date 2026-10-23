# Paper Trail

A tenant evidence log you talk to. Say "the ceiling in the bedroom is leaking again" and Paper Trail stores a timestamped, **tamper-evident** record. Roommates add to the same record. When the landlord goes quiet, it drafts the letter from the record.

Built for the Build, Ship, Shape: Amazon Developer Hackathon, **Alexa+ track** (MCP-based, simulated Alexa+ experience).

**Live demo:** https://3-224-186-234.sslip.io/simulator (demo data only; access is filled in for you). Typing works in every browser. Voice input uses the browser's speech recognition, so it needs Chrome, Edge or Safari, and a secure page or localhost.

**Not legal advice.**

## What it does

- Logs problems by conversation: it asks which room and what is wrong, then **proposes the entry and waits for a yes** before anything is written.
- Tracks landlord contacts and user-entered deadlines per issue.
- Answers questions about the record ("When did I first tell the landlord?", "Did Amina and I disagree about anything?") using only the facts in the record, and says "I don't have that in your record" when it isn't there.
- Drafts a letter for the most urgent open issue. The letter stays a draft until the user confirms it was sent.
- Builds a printable evidence packet.
- Verifies the hash chain and names exactly which entry was altered.

## How the AI is used

Amazon Bedrock with Claude Haiku 4.5, in three roles:

1. **Understands the message**: chat, a question about the record, or a problem report. For a report it fills a fixed form (room, category, description, dates).
2. **Reads problem reports** into structured fields, checked against a fixed vocabulary.
3. **Answers questions** from the record's facts, with the last few turns for context.

What the model **cannot** do:

- It has no write access. A report becomes a proposal, signed server-side and valid for 15 minutes. Only a spoken or clicked "yes" turns a valid proposal into ledger writes. A forged or expired confirmation writes nothing (covered by tests).
- The service refuses empty or placeholder rooms and descriptions, so a guess never becomes a permanent entry.
- Deadlines are always user-entered. No jurisdiction's law is hard-coded.

If Bedrock fails or the daily call limit is reached, the app falls back to an offline rule-based parser, so everything still works.

## Why it is not a CRUD app

A deterministic reasoning layer sits over an append-only log:

- Recurrence detection ("third leak in this room in 90 days")
- Response clock against a deadline the user enters
- Escalation ladder: reminder, letter draft, evidence packet
- Evidence completeness score
- Conflict flags when roommates' accounts differ
- Ranking of open issues by urgency

Rules decide all of the above.

## What is real and what is simulated

The server is real: a Streamable HTTP MCP server (spec 2025-11-25, MCP Python SDK) exposing 14 tools. The demo drives it through a **simulated Alexa+ web client** (source in this repo, labeled as simulated in the UI). No Alexa device or Alexa+ service is used. In an Alexa+ deployment, the MCP server is the tool layer and Alexa+ is the voice front end.

MCP tools: `log_issue`, `add_update`, `record_landlord_contact`, `set_deadline`, `resolve_issue`, `correct_entry`, `whats_open`, `issue_timeline`, `record_facts`, `draft_letter`, `confirm_letter_sent`, `evidence_packet`, `ledger_view`, `verify_integrity`.

## Architecture

```
config/          composition root: Starlette owns the lifespan; /mcp -> MCP SDK app; the rest -> Django
mcp_server/      thin MCP adapter: identity, one service call, speech formatting
ledger/
  domain/        pure Python (hash chain, vocabulary)
  models/        Django models, append-only
  services/      use cases: the only place business actions happen
engine/          pure rules: recurrence, deadlines, completeness, escalation, letters
ai/              Bedrock parser, conversation decider, answerer; offline fallbacks; call budget
api/             Django Ninja: /api/chat, packet, ledger view, and the simulator page
render/          printable evidence packet
```

Flow: browser -> `/api/chat` -> rules or Bedrock decide -> MCP server tools -> ledger.

### Tamper evidence

Each entry stores a SHA-256 hash of its contents plus the previous entry's hash. Editing an entry breaks its own hash, and rewriting a hash breaks the next link. Entries cannot be updated or deleted through the app, and a Postgres trigger blocks raw SQL edits. Corrections are new entries.

This is tamper-**evident**, not tamper-proof: someone with full database access could rewrite the whole chain. Anchoring the head hash outside the database is on the roadmap.

## Run locally

Requires Python 3.12, Docker, and a free port 8000.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
docker compose up -d
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
make seed     # demo household with a three-leak story; prints a demo token
make run      # MCP server and web app on http://localhost:8000
```

Open http://localhost:8000/simulator, paste the token under **Access**, and try:

- `What's open?`
- `I have a new problem`, then `the bathroom`, then `the tap won't stop dripping`, then `yes`
- `When did I first tell the landlord?`
- `Draft a letter`
- `Is my record intact?`

Without AWS credentials the app runs fully offline with the rule-based parser. Run the tests with `make test`.

### Turn on Bedrock

```bash
export PAPER_TRAIL_PARSER=bedrock
export AWS_REGION=us-east-1
# optional: BEDROCK_MODEL_ID (default: us.anthropic.claude-haiku-4-5-20251001-v1:0)
# optional: AI_DAILY_CALL_LIMIT (default 100)
```

The AWS identity needs `bedrock:InvokeModel` on the model. Credentials come from the standard AWS chain, never from the repo.

## Safety

No jurisdiction's law is hard-coded. All demo data and addresses are fake. This project does not provide legal advice.

## License

MIT, see `LICENSE`.
