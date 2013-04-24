from devparrot import capi
from devparrot.capi import Command
from devparrot.capi.constraints import Boolean

@Command(
vertical = Boolean(default= lambda : False)
)
def split(vertical):
    """split the view it two separate panes"""
    capi.split(vertical)

@Command()
def unsplit():
    """unsplit (merge) two separate panes"""
    capi.unsplit()

