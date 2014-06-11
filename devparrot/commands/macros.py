

from devparrot.core.command import Command, Macro, Alias

from devparrot.core.ui.viewContainer import get_neighbour

def _get_neighbour(direction):
    from devparrot.core import session
    neighbour = get_neighbour(session.get_currentContainer(), direction)
    if neighbour:
        return neighbour.document.title
    return ""


@Macro()
def previous():
    return _get_neighbour("previous")

@Macro()
def next():
    return _get_neighbour("next")

@Macro()
def left():
    return _get_neighbour("left")

@Macro()
def right():
    return _get_neighbour("right")

@Macro()
def top():
    return _get_neighbour("top")

@Macro()
def bottom():
    return _get_neighbour("bottom")

@Macro()
def current():
    from devparrot.core import session
    return session.get_currentDocument().title

@Macro()
def all_document():
    from devparrot.core import session
    return [d.title for d in session.get_documentManager()]
