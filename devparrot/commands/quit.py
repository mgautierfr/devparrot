from devparrot.core.command.baseCommand import Command
from devparrot.core import capi

@Command()
def quit():
    """quit devparrot"""
    while len(capi.documents):
        capi.close_document(capi.get_nth_file(0))
    capi.quit()
