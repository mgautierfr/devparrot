from devparrot.core.command import Command
from devparrot.core import constraints, capi

@Command(
document = constraints.OpenDocument()
)
def switch(document):
    """set focus to document"""
    capi.currentDocument = document

