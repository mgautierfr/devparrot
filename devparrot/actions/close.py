from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

class close(Command):
    documents = constraints.OpenDocument(multiple=True, default=lambda:capi.currentDocument)
    def pre_check(cls):
        return capi.currentDocument is not None

    def run(cls, documents, *args):
        for document in documents:
            capi.close_document(document)
        return True

class closeall(Command):
    def run(cls, *args):
        ret = True
        while len(capi.documents):
            ret = ret and capi.close_document(capi.get_nth_file(0))
        return ret

