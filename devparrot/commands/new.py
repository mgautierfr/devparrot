from devparrot.core.command import Command
from devparrot.core import constraints
from devparrot.core.session import bindings
from devparrot.core import capi

@Command(
content = constraints.Stream()
)
def new(content):
    """
    Create a new document

    Content is inserted in the document once created
    """
    from devparrot.core.document import Document
    from devparrot.documents.newDocSource import NewDocSource
    document = Document(NewDocSource())
    capi.add_file(document)
    capi.currentDocument = document
    model = document.get_model()

    for line in content:
        model.insert("insert", line)

bindings["<Control-n>"] = "new\n"
