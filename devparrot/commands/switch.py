from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi


class switch(Command):
    document = constraints.OpenDocument()
    def run(cls, document, *args):
        capi.currentDocument = document
        return True

