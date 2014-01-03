

from devparrot import capi
from devparrot.capi import Command, constraints, Macro, Alias
from functools import partial

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
    return session.get_currentDocument().title


@Macro(configEntry= constraints.ConfigEntry())
def config(configEntry):
    return configEntry.get()
