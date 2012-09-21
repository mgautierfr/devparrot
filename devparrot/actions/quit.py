from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi
import close

class quit(Command):
    def run(cls, *args):
        while len(capi.documents):
            close.close_a_document(capi.get_nth_file(0))
        return capi.quit()
