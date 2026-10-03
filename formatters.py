from collections.abc import Callable
from functools import cache

import things

def format_todo(todo: dict, *, lookup: Callable[[str], dict | None] | None = None) -> str:
    """Helper function to format a single todo into a readable string."""
    lookup = lookup or things.get
    todo_text = f"Title: {todo['title']}"
    
    # Add UUID for reference
    todo_text += f"\nUUID: {todo['uuid']}"
    
    # Add type
    todo_text += f"\nType: {todo['type']}"
    
    # Add status if present
    if todo.get('status'):
        todo_text += f"\nStatus: {todo['status']}"
        
    # Add start/list location
    if todo.get('start'):
        todo_text += f"\nList: {todo['start']}"

    # Add dates
    if todo.get('start_date'):
        todo_text += f"\nStart Date: {todo['start_date']}"
    if todo.get('deadline'):
        todo_text += f"\nDeadline: {todo['deadline']}"
    if todo.get('stop_date'):  # Completion date
        todo_text += f"\nCompleted: {todo['stop_date']}"
    
    # Add notes if present
    if todo.get('notes'):
        todo_text += f"\nNotes: {todo['notes']}"
    
    for field, label in (("project", "Project"), ("heading", "Heading"), ("area", "Area")):
        if todo.get(field):
            try:
                related = lookup(todo[field])
                if related:
                    todo_text += f"\n{label}: {related['title']}"
            except Exception:
                # A stale related item must not hide the task itself.
                pass

    # Add tags if present
    if todo.get('tags'):
        todo_text += f"\nTags: {', '.join(todo['tags'])}"
    
    # Add checklist if present and contains items
    if isinstance(todo.get('checklist'), list):
        todo_text += "\nChecklist:"
        for item in todo['checklist']:
            status = "✓" if item['status'] == 'completed' else "□"
            todo_text += f"\n  {status} {item['title']}"
    
    return todo_text


def format_todos(todos: list[dict] | None, empty_message: str = "No items found") -> str:
    """Format one response, reusing related-item lookups only within that response."""
    if not todos:
        return empty_message
    lookup = cache(things.get)
    return "\n\n---\n\n".join(format_todo(todo, lookup=lookup) for todo in todos)


def format_project(project: dict, include_items: bool = False) -> str:
    """Helper function to format a single project."""
    project_text = f"Title: {project['title']}\nUUID: {project['uuid']}"
    
    if project.get('area'):
        try:
            area = things.get(project['area'])
            if area:
                project_text += f"\nArea: {area['title']}"
        except Exception:
            pass
            
    if project.get('notes'):
        project_text += f"\nNotes: {project['notes']}"
    
    # Always show headings for projects
    headings = things.tasks(type='heading', project=project['uuid'])
    if headings:
        project_text += "\n\nHeadings:"
        for heading in headings:
            project_text += f"\n- {heading['title']}"
        
    if include_items:
        todos = things.todos(project=project['uuid'])
        if todos:
            project_text += "\n\nTasks:"
            for todo in todos:
                project_text += f"\n- {todo['title']}"
    
    return project_text

def format_area(area: dict, include_items: bool = False) -> str:
    """Helper function to format a single area."""
    area_text = f"Title: {area['title']}\nUUID: {area['uuid']}"
    
    if area.get('notes'):
        area_text += f"\nNotes: {area['notes']}"
        
    if include_items:
        projects = things.projects(area=area['uuid'])
        if projects:
            area_text += "\n\nProjects:"
            for project in projects:
                area_text += f"\n- {project['title']}"
                
        todos = things.todos(area=area['uuid'])
        if todos:
            area_text += "\n\nTasks:"
            for todo in todos:
                area_text += f"\n- {todo['title']}"
    
    return area_text

def format_tag(tag: dict, include_items: bool = False) -> str:
    """Helper function to format a single tag."""
    tag_text = f"Title: {tag['title']}\nUUID: {tag['uuid']}"
    
    if tag.get('shortcut'):
        tag_text += f"\nShortcut: {tag['shortcut']}"
        
    if include_items:
        todos = things.todos(tag=tag['title'])
        if todos:
            tag_text += "\n\nTagged Items:"
            for todo in todos:
                tag_text += f"\n- {todo['title']}"
    
    return tag_text

def format_heading(heading: dict, include_items: bool = False) -> str:
    """Helper function to format a single heading."""
    heading_text = f"Title: {heading['title']}\nUUID: {heading['uuid']}"
    heading_text += "\nType: heading"
    
    # Add project info if present
    if heading.get('project'):
        if heading.get('project_title'):
            heading_text += f"\nProject: {heading['project_title']}"
        else:
            try:
                project = things.get(heading['project'])
                if project:
                    heading_text += f"\nProject: {project['title']}"
            except Exception:
                pass
    
    # Add dates
    if heading.get('created'):
        heading_text += f"\nCreated: {heading['created']}"
    if heading.get('modified'):
        heading_text += f"\nModified: {heading['modified']}"
        
    # Add notes if present
    if heading.get('notes'):
        heading_text += f"\nNotes: {heading['notes']}"
        
    if include_items:
        # Get todos under this heading
        todos = things.todos(heading=heading['uuid'])
        if todos:
            heading_text += "\n\nTasks under heading:"
            for todo in todos:
                heading_text += f"\n- {todo['title']}"
    
    return heading_text
