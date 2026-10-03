import json
from pathlib import Path

import pytest

from things_server import mcp


EXPECTED_TOOLS = {'get_inbox': ([], []),
 'get_today': ([], []),
 'get_upcoming': ([], []),
 'get_anytime': ([], []),
 'get_someday': ([], []),
 'get_logbook': (['period', 'limit'], []),
 'get_trash': ([], []),
 'get_todos': (['project_uuid', 'include_items'], []),
 'get_projects': (['include_items'], []),
 'get_areas': (['include_items'], []),
 'get_tags': (['include_items'], []),
 'get_tagged_items': (['tag'], ['tag']),
 'get_headings': (['project_uuid'], []),
 'search_todos': (['query'], ['query']),
 'search_advanced': (['status', 'start_date', 'deadline', 'tag', 'area', 'type'], []),
 'get_recent': (['period'], ['period']),
 'add_todo': (['title',
               'notes',
               'when',
               'deadline',
               'tags',
               'checklist_items',
               'list_id',
               'list_title',
               'heading',
               'heading_id'],
              ['title']),
 'add_project': (['title', 'notes', 'when', 'deadline', 'tags', 'area_id', 'area_title', 'todos'],
                 ['title']),
 'update_todo': (['id',
                  'title',
                  'notes',
                  'when',
                  'deadline',
                  'tags',
                  'completed',
                  'canceled',
                  'list',
                  'list_id',
                  'heading',
                  'heading_id'],
                 ['id']),
 'update_project': (['id', 'title', 'notes', 'when', 'deadline', 'tags', 'completed', 'canceled'],
                    ['id']),
 'show_item': (['id', 'query', 'filter_tags'], ['id']),
 'search_items': (['query'], ['query'])}


@pytest.mark.asyncio
async def test_registered_tools_preserve_names_parameters_and_required_fields():
    tools = await mcp.get_tools()
    assert set(tools) == set(EXPECTED_TOOLS)
    manifest = json.loads((Path(__file__).resolve().parents[1] / "manifest.json").read_text())
    assert {tool["name"] for tool in manifest["tools"]} == set(tools)
    for name, (parameters, required) in EXPECTED_TOOLS.items():
        schema = tools[name].parameters
        assert set(schema["properties"]) == set(parameters)
        assert schema.get("required", []) == required


@pytest.mark.asyncio
async def test_optional_tool_parameters_advertise_null_defaults():
    for tool in (await mcp.get_tools()).values():
        for schema in tool.parameters["properties"].values():
            if "default" in schema and schema["default"] is None:
                assert {"type": "null"} in schema.get("anyOf", [])
