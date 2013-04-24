from devparrot.capi import Command
from devparrot.core.session import bindings
from devparrot.capi.constraints import OpenDocument
from devparrot import capi


@Command(
    documents = OpenDocument(default=capi.get_currentDocument, help="documents to close")
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

bindings["<Control-w>"] = "close\n"
