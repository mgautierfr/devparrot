from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

@Command(
document = constraints.OpenDocument()
)
def switch(document):
    """set focus to document"""
    capi.currentDocument = document

