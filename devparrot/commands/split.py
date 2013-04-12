from devparrot.core.command import Command
from devparrot.core import constraints, capi

@Command(
vertical = constraints.Boolean(default= lambda : False)
)
def split(vertical):
    """split the view it two separate panes"""
    capi.split(vertical)

@Command()
def unsplit():
    """unsplit (merge) two separate panes"""
    capi.unsplit()

