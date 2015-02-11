

from devparrot.core.command import Command, Macro
from devparrot.core.errors import InvalidArgument

from devparrot.core.ui.viewContainer import get_neighbour

def _get_neighbour(direction):
    from devparrot.core import session
    currentContainer = get_neighbour(session.get_currentContainer(), direction)
    if currentContainer is None:
        raise InvalidArgument()
    return currentContainer.document

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
    currentDoc = session.get_currentDocument()
    if currentDoc is None:
        raise InvalidArgument()
    return currentDoc

@Macro()
def all_document():
    from devparrot.core import session
    return list(session.get_documentManager())


@Macro()
def range(text):
    from devparrot.core.constraints import Range
    ok, result = Range().check(text)

    if ok:
        doc, range_ = result
        return doc.get_model().get(str(range_.first), str(range_.last))
    raise InvalidArgument()
