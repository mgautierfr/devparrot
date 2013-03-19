from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

@Command(
document = constraints.OpenDocument()
)
def switch(document):
    capi.currentDocument = document

