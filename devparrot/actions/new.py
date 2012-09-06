from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, capi


class new(Command):
    def run(cls, *args):
        from devparrot.core.document import Document
        from devparrot.documents.newDocSource import NewDocSource
        document = Document(NewDocSource())
        capi.add_file(document)
        capi.currentDocument = document
        return True

