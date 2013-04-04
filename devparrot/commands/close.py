from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi


@Command(
    documents = constraints.OpenDocument(default=lambda:capi.currentDocument, help="documents to close")
)
def close(*documents):
    "close one or several documents"
    for document in documents:
        capi.close_document(document)

@Command()
def closeall():
    """close all opened documents"""
    while len(capi.documents):
        capi.close_document(capi.get_nth_file(0))

binder["<Control-w>"] = "close\n"
