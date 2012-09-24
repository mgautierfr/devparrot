from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

def close_a_document(document):
    if document.check_for_save():
        save.save_document(document)
    if document.documentView.is_displayed():
        parentContainer = document.documentView.get_parentContainer()
        parentContainer.detach_child(document.documentView)
        if parentContainer.get_nbChildren() == 0:
            capi.unsplit(parentContainer)
    capi.del_file(document)

class close(Command):
    documents = constraints.OpenDocument(multiple=True, default=lambda:capi.currentDocument)
    def pre_check(cls):
        return capi.currentDocument is not None

    def run(cls, documents, *args):
        for document in documents:
            close_a_document(document)
        return True

class closeall(Command):
    def run(cls, *args):
        ret = True
        while len(capi.documents):
            ret = ret and close_a_document(capi.get_nth_file(0))
        return ret

