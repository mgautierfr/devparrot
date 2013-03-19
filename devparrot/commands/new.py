from devparrot.core.command.baseCommand import Command
from devparrot.core.command import binder
from devparrot.core import capi

@Command()
def new():
    from devparrot.core.document import Document
    from devparrot.documents.newDocSource import NewDocSource
    document = Document(NewDocSource())
    capi.add_file(document)
    capi.currentDocument = document

binder["<Control-n>"] = "new\n"
