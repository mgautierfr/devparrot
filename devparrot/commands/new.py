from devparrot import capi
from devparrot.capi import Command
from devparrot.capi import constraints
from devparrot.core.session import bindings


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
    capi.set_currentDocument(document)
    model = document.get_model()

    for line in content:
        model.insert("insert", line)

bindings["<Control-n>"] = "new\n"
