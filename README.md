# Paper Trail

A tenant evidence log you talk to. Say "the ceiling in the bedroom is leaking again" and the server stores a timestamped, **tamper-evident** record. Roommates can add to the same record. **Not legal advice.**

Built for the Build, Ship, Shape: Amazon Developer Hackathon (Alexa+ track).

## Why it is not a CRUD app

The value is a deterministic reasoning layer over an append-only log:

- Recurrence detection ("third leak in this room this quarter")
- Response clock against a deadline the user enters
- Escalation ladder: reminder, letter draft, evidence packet
- Evidence completeness score
- Conflict flags when roommates' accounts differ
- Integrity check: recompute the hash chain and name exactly which entry was altered

Rules decide all of the above. The LLM (Amazon Bedrock) only parses speech into structured entries, asks clarifying questions, and drafts wording. Letters stay drafts until the user confirms they were sent.

## Status

<!-- STATUS:START -->
Built and verified:

- Append-only hash-chain ledger (per-household sequence, unique constraint, row lock on append, ORM and Postgres-trigger protection)
- `verify_chain` names the exact altered, missing or re-linked entry
- MCP server over Streamable HTTP at `/mcp` (protocol 2025-11-25, MCP Python SDK 1.30.x, stateless)
- MCP tool: `log_issue`
- 8 tests passing

Not built yet: other tools, rules engine, Bedrock parsing, letters, evidence packet, share links, simulator, deploy.
<!-- STATUS:END -->

## What is real and what is simulated

Alexa+ access path: **TBD** (to be confirmed against the official Resources page). If the demo uses a simulated Alexa+ experience, the simulator source will be in this repo and every simulated part will be labeled here.

## Architecture

```
config/        composition root: Starlette owns the lifespan; /mcp -> MCP SDK app; everything else -> Django
mcp_server/    thin MCP adapter: identity, one service call, speech formatting
ledger/
  domain/      pure Python (hash chain, vocab): no Django, no MCP
  models/      Django models, append-only
  services/    use cases: the only place business actions happen
engine/        (planned) pure rules: recurrence, deadlines, completeness, escalation
api/           (planned) Django Ninja: simulator chat, share page, health
```

Rules of the road: adapters stay thin, rules decide, the LLM only parses and drafts, files stay under 200 lines.

### Tamper evidence

Each entry stores a SHA-256 hash of its contents plus the previous entry's hash. Editing any entry breaks its own hash, and rewriting a hash breaks the next link. Entries cannot be updated or deleted through the app, and a Postgres trigger blocks raw SQL edits too. Corrections are new entries.

This is tamper-**evident**, not tamper-proof: someone with full database access could rewrite the whole chain. Anchoring the head hash outside the database is planned.

## Run locally

Requires Python 3.12, Docker, and a free port 8000.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
docker compose up -d
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
make run
```

Check it:

```bash
curl -s localhost:8000/health
curl -s -X POST localhost:8000/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"log_issue","arguments":{"room":"Bedroom","category":"leak","description":"Ceiling is leaking again near the window"}}}'
```

Or use the MCP Inspector: `npx @modelcontextprotocol/inspector`, transport Streamable HTTP, URL `http://localhost:8000/mcp`.

Run the tests: `make test`

## Safety

Deadlines are always user-entered. No jurisdiction's law is hard-coded. All demo data and addresses are fake. This project does not provide legal advice.

## License

MIT, see `LICENSE`.
