from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

def _get_default():
    if capi.currentDocument is None:
        raise constraints.noDefault()
    if capi.currentDocument.has_a_path():
        return capi.currentDocument.get_path()
    raise constraints.noDefault()
        
@Command(
fileName = constraints.File(mode=constraints.File.SAVE, default=lambda:_get_default())
)
def save(fileName):
    capi.save_document(capi.currentDocument, fileName)

@Command(
fileName = constraints.File(mode=constraints.File.SAVE)
)
def saveas(fileName):
    capi.save_document(capi.currentDocument, fileName)

binder["<Control-s>"] = "save\n"
binder["<Control-Shift-S>"] = "saveas\n"
