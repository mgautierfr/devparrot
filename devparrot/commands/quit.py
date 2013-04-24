from devparrot import capi
from devparrot.capi import Command


@Command()
def quit():
    """quit devparrot"""
    while len(capi.documents):
        capi.close_document(capi.get_nth_file(0))
    capi.quit()
