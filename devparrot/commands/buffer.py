from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core.commandLauncher import create_section
from devparrot.core import capi

def buffer(name, content):
    """Open a buffer and fill it with comment

A buffer is not attach to any file and can't be modified"""
    from devparrot.core.document import Document
    from devparrot.documents.bufferSource import BufferSource
    document = Document(BufferSource(name))
    capi.add_file(document)
    capi.currentDocument = document
    model = document.get_model()

    for line in content:
        model.insert("insert", line)


Command(
content = constraints.Stream()
)(buffer, create_section("capi"))
