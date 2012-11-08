from devparrot.core.command.baseCommand import Command
from devparrot.core import capi

class quit(Command):
    def run(cls, *args):
        while len(capi.documents):
            capi.close_document(capi.get_nth_file(0))
        return capi.quit()
