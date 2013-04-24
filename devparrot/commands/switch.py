from devparrot.capi import Command, set_currentDocument
from devparrot.capi.constraints import OpenDocument

@Command(
document = OpenDocument()
)
def switch(document):
    """set focus to document"""
    set_currentDocument(document)

