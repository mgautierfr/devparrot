from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

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

