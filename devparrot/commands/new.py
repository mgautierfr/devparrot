from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

@Command(
content = constraints.Stream()
)
def new(content):
    from devparrot.core.document import Document
    from devparrot.documents.newDocSource import NewDocSource
    document = Document(NewDocSource())
    capi.add_file(document)
    capi.currentDocument = document
    model = document.get_model()

    for line in content:
        model.insert("insert", line)

binder["<Control-n>"] = "new\n"
