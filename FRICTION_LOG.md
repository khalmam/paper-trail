# Friction log

Format: task attempted | steps | expected vs actual | severity (1-5) | workaround | suggestion

## 3. Test-database teardown warning after an async MCP tool test
- Task: run the pytest suite including an async test that calls an MCP tool through sync_to_async.
- Expected: clean teardown. Actual: 'database "test_papertrail" is being accessed by other users'.
- Severity: 1 (all tests pass). Workaround: none needed; the next run recreates the DB.
- Suggestion: document how thread-pool DB connections interact with pytest-django teardown.

## Known limits, to revisit after the first finish (Oct 17)
- The parser handles one problem per sentence; several facts in one sentence (issue, contact, deadline) are not split yet.
- The offline keyword parser misses sentences like "the AC is not cooling"; the Bedrock parser covers them.
- Categories are a fixed list (with "other") so recurrence counting stays trustworthy.
- Voice uses the browser's speech recognition: Chrome and Safari only, and it needs HTTPS once deployed.
