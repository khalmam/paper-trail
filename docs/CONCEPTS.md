# Concepts used in Paper Trail

- **ASGI lifespan**: startup/shutdown phase of an async server. The MCP SDK needs it; Starlette provides it (`config/asgi.py`).
- **MCP over Streamable HTTP**: AI clients discover typed tools and call them over HTTP. Stateless mode keeps no server session; state lives in Postgres.
- **sync_to_async**: runs blocking Django ORM code in a worker thread so async tools never block the event loop (`mcp_server/runner.py`).
- **Row lock (`select_for_update`)**: makes concurrent appends take turns so sequence numbers never collide.
- **Hash chain**: each entry hashes its contents plus the previous hash; altering anything breaks verification at that entry.
- **Append-only, twice**: ORM blocks edits, and a Postgres trigger blocks raw SQL edits.
- **Context variable**: per-request storage that async code can read; used to pass the bearer token to tools.
- **Token hashing**: only a SHA-256 of each access token is stored; the raw token is shown once.
- **Architecture test**: a test that reads imports and fails when a layer crosses a boundary.
