from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core.errors import NoDefault
from devparrot.core import capi

def _get_default():
    if capi.currentDocument is None:
        raise NoDefault()
    if capi.currentDocument.has_a_path():
        return capi.currentDocument.get_path()
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
        capi.save_document(capi.currentDocument, fileName)
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
        capi.save_document(capi.currentDocument, fileName)
    except IOError:
        raise FileAccessError(fileName)

binder["<Control-s>"] = "save\n"
binder["<Control-Shift-S>"] = "saveas\n"
