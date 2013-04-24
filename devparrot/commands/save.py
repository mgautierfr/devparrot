from devparrot.capi import Command, get_currentDocument, save_document
from devparrot.capi import constraints
from devparrot.core.session import bindings
from devparrot.core.errors import NoDefault

def _get_default():
    if get_currentDocument() is None:
        raise NoDefault()
    if get_currentDocument().has_a_path():
        return get_currentDocument().get_path()
    raise NoDefault()
        
@Command(
fileName = constraints.File(mode=constraints.File.SAVE, default=lambda:_get_default())
)
def save(fileName):
    """
    Save current file.

    If fileName is provided, act as "saveas" command.
    """
    try:
        save_document(get_currentDocument(), fileName)
    except IOError:
        raise FileAccessError(fileName)

@Command(
fileName = constraints.File(mode=constraints.File.SAVE)
)
def saveas(fileName):
    """
    Save current file to fileName.

    If fileName is not provided, the user is asked for it.
    """
    try:
        save_document(get_currentDocument(), fileName)
    except IOError:
        raise FileAccessError(fileName)

bindings["<Control-s>"] = "save\n"
bindings["<Control-Shift-S>"] = "saveas\n"
