import pytest
from things_server import get_todos, get_today, search_todos


@pytest.mark.asyncio
async def test_get_todos_includes_checklist(mocker, mock_todo):
    mock_things_todos = mocker.patch('things.todos')
    mock_things_todos.return_value = [mock_todo]

    result = await get_todos.fn(include_items=True)

    assert "Checklist:" in result
    assert "First item" in result
    mock_things_todos.assert_called_once_with(project=None, start=None, include_items=True)


@pytest.mark.asyncio
async def test_get_today_includes_checklist(mocker, mock_todo):
    mock_today = mocker.patch('things.today')
    mock_today.return_value = [mock_todo]

    result = await get_today.fn()

    assert "Checklist:" in result
    assert "First item" in result
    mock_today.assert_called_once_with(include_items=True)


@pytest.mark.asyncio
async def test_search_todos_includes_checklist(mocker, mock_todo):
    mock_search = mocker.patch('things.search')
    mock_search.return_value = [mock_todo]

    result = await search_todos.fn("Test")

    assert "Checklist:" in result
    assert "First item" in result
    mock_search.assert_called_once_with("Test", include_items=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('item_type', ['to-do', 'project', 'heading'])
async def test_advanced_search_routes_explicit_types_to_tasks(mocker, item_type):
    from things_server import search_advanced

    tasks = mocker.patch('things.tasks', return_value=[])
    todos = mocker.patch('things.todos', side_effect=AssertionError('Duplicate type keyword'))
    result = await search_advanced.fn(type=item_type, tag='work')
    assert result == 'No matching todos found'
    tasks.assert_called_once_with(include_items=True, type=item_type, tag='work')
    todos.assert_not_called()


@pytest.mark.asyncio
async def test_advanced_search_without_type_still_returns_todos(mocker):
    from things_server import search_advanced

    todos = mocker.patch('things.todos', return_value=[])
    assert await search_advanced.fn(tag='work') == 'No matching todos found'
    todos.assert_called_once_with(include_items=True, tag='work')
