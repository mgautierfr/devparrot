from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

class save(Command):
    @staticmethod
    def get_default():
        if capi.currentDocument is None:
            raise constraints.noDefault()
        if capi.currentDocument.has_a_path():
            return capi.currentDocument.get_path()
        raise constraints.noDefault()

    fileName = constraints.File(mode=constraints.File.SAVE, default=lambda:save.get_default())

    def pre_check(cls):
        return capi.currentDocument is not None

    def run(cls, fileName, *args):
        return save.save_document(capi.currentDocument,fileName)

    @staticmethod
    def save_document(document, fileToSave):
        if document.has_a_path() and document.get_path() == fileToSave:
                return document.write()

        if capi.file_is_opened(fileToSave):
            #The document is already opened.
            #do nothing (should warn)
            return False

        from devparrot.documents.fileDocSource import FileDocSource
        document.set_path(FileDocSource(fileToSave))
        return document.write()


