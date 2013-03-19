from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

@Command(
vertical = constraints.Boolean(default= lambda : False)
)
def split(vertical):
    capi.split(vertical)

@Command()
def unsplit():
    capi.unsplit()

