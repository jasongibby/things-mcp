# Development notes

This macOS MCP server reads Things 3 through `things-py` and submits changes through
the Things URL scheme. All 22 public tool names, parameter names and text response
formats are compatibility contracts.

## Commands

```bash
uv sync --locked --extra test
uv run pytest
uv run things_server.py
```

The test suite mocks Things database reads and URL execution. Never exercise write
tools against the live application as a routine test. A successful URL submission
is not a database readback; after a timeout, check Things before retrying a mutation.

## Files and conventions

- `things_server.py`: tool definitions and query routing. Keep optional types aligned
  with their defaults so generated schemas accept explicit nulls.
- `formatters.py`: human-readable responses. Todo-list lookups are cached within one
  response only; do not introduce a persistent cache of mutable Things data.
- `url_scheme.py`: URL encoding, update authentication and dispatch. Do not log URLs
  or auth tokens. Pass URLs as AppleScript arguments, never interpolate script text.
- `manifest.json`: desktop extension metadata and tool inventory.
- `build_dxt.sh`: bundles locked runtime dependencies and stages a DXT package in an
  isolated temporary directory. Requires `uv`, Python 3.12+, and `dxt` on PATH.
- `tests/`: unit, schema contract and isolated package-assembly tests.

Dependencies belong in `pyproject.toml` and `uv.lock`; the package build exports the
lockfile instead of maintaining another dependency list. `httpx` is transitive via
FastMCP, not a direct application dependency. Calendar/Things permission or protocol
errors should remain actionable without exposing task contents or credentials.
