from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

@Command(
    documents = constraints.OpenDocument(default=lambda:capi.currentDocument)
)
def close(*documents):
    for document in documents:
        capi.close_document(document)
    return True

@Command()
def closeall():
    ret = True
    while len(capi.documents):
        ret = ret and capi.close_document(capi.get_nth_file(0))
    return ret

binder["<Control-w>"] = "close\n"
