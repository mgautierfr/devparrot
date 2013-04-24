from devparrot import capi
from devparrot.capi import Command, create_section
from devparrot.capi.constraints import Stream


def buffer(name, content):
    """Open a buffer and fill it with comment

A buffer is not attach to any file and can't be modified"""
    from devparrot.core.document import Document
    from devparrot.documents.bufferSource import BufferSource
    document = Document(BufferSource(name))
    capi.add_file(document)
    capi.set_currentDocument(document)
    model = document.get_model()

    for line in content:
        model.insert("insert", line)


Command(content=Stream())(buffer, create_section("capi"))
