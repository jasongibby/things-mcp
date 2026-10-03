# Things MCP Server

An MCP server for Things 3 on macOS. It reads tasks through
[Things.py](https://github.com/thingsapi/things.py) and creates or updates them through
the [Things URL scheme](https://culturedcode.com/things/help/url-scheme/). It works
with MCP clients that support stdio, including Claude Desktop and Claude Code.

## Tools

| Group | Tools |
| --- | --- |
| Lists | `get_inbox`, `get_today`, `get_upcoming`, `get_anytime`, `get_someday`, `get_logbook`, `get_trash` |
| Items | `get_todos`, `get_projects`, `get_areas`, `get_headings`, `get_recent` |
| Tags | `get_tags`, `get_tagged_items` |
| Search | `search_todos`, `search_advanced` |
| Create/update | `add_todo`, `add_project`, `update_todo`, `update_project` |
| Things interface | `show_item`, `search_items` |

Read tools return text with item IDs and available details, including checklists.
`show_item` and `search_items` open the Things interface; use `search_todos` to return
search results to the client.

- `get_todos` accepts an optional `project_uuid` and includes checklist items by default.
- `get_projects`, `get_areas`, and `get_tags` accept `include_items` (default `false`).
- `get_headings` accepts an optional `project_uuid`.
- `get_logbook` defaults to the last `7d`, with a limit of `50` entries.
- `get_recent` accepts a period such as `3d`, `1w`, `2m`, or `1y`.
- `search_advanced` filters by `status`, `start_date`, `deadline`, `tag`, `area`, and `type`.
- Create and update tools expose scheduling, notes, tags and other supported fields
  in their input schemas. Updates automatically retrieve the Things auth token.

Writes submit a Things URL. They do not return a newly created item's ID or verify
that the application has persisted the change. If a request times out, inspect
Things before retrying to avoid duplicate changes.

## Installation

Requires macOS with Things 3 installed and opened at least once. Enable Things URLs
in Things settings. Source installations require Python 3.12+ and
[uv](https://docs.astral.sh/uv/).

### Desktop extension

Download the `.dxt` package from the [releases page](https://github.com/hald/things-mcp/releases)
and open it in a compatible desktop client. The package contains its Python dependencies.

### From source

```bash
git clone https://github.com/hald/things-mcp
cd things-mcp
uv sync --locked
```

Configure your client to run `uv --directory /absolute/path/to/things-mcp run things_server.py`.
For clients using an `mcpServers` configuration, such as Claude Desktop:

```json
{
  "mcpServers": {
    "things": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/things-mcp", "run", "things_server.py"]
    }
  }
}
```

For Claude Code:

```bash
claude mcp add-json things '{"command":"uv","args":["--directory","/absolute/path/to/things-mcp","run","things_server.py"]}'
```

Add `-s user` to the Claude Code command for all projects. Replace the source path
with the actual absolute path. If the client cannot find `uv`, use the full path
returned by `command -v uv`. Restart the client, then try “What's in my Things inbox?”

For updates, pull the source changes, run `uv sync --locked`, and restart the client.

## Development

```bash
uv sync --locked --extra test
uv run pytest
```

Tests cover URL encoding and dispatch, formatting, tool registration, and package
assembly without writing to Things. Todo formatting reuses related-item lookups
within one response, so later requests see changes in Things.

Build a desktop extension on the target macOS architecture with Python 3.12+, `uv`,
and the `dxt` CLI on PATH:

```bash
./build_dxt.sh
```

The script exports the lockfile's runtime dependencies, checks package hashes, and
stages the extension in a temporary directory. Output goes to `dist/`; previous
packages are retained. Test dependencies are excluded. Native wheels in the bundle
must match the Python runtime and architecture of the client running it.

Implementation and maintenance notes are in [CLAUDE.md](CLAUDE.md).

## Troubleshooting

- Open Things at least once so its local database exists.
- Enable Things URLs before using create or update tools.
- Verify that your MCP configuration uses the correct absolute source and `uv` paths.
- Run `uv sync --locked` if modules are missing.
- Check the client's MCP logs for startup errors. Claude Desktop logs are under
  `~/Library/Logs/Claude/`.

## License and support

[MIT](LICENSE). Original project by Hal Dick; [support the author](https://ko-fi.com/haldick).
