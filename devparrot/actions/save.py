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
        return capi.save_document(capi.currentDocument, fileName)

