# Friction log

Format: task attempted | steps | expected vs actual | severity (1-5) | workaround | suggestion

## 3. Test-database teardown warning after an async MCP tool test
- Task: run the pytest suite including an async test that calls an MCP tool through sync_to_async.
- Expected: clean teardown. Actual: 'database "test_papertrail" is being accessed by other users'.
- Severity: 1 (all tests pass). Workaround: none needed; the next run recreates the DB.
- Suggestion: document how thread-pool DB connections interact with pytest-django teardown.
