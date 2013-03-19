from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

lastSearch = None

@Command(
    searchText = constraints.Default(default=lambda : lastSearch),
    backward = constraints.Boolean(default=lambda : False)
)
def search(searchText, backward):
    global lastSearch
    lastSearch = searchText
    if searchText:
        capi.currentDocument.search(backward, searchText)

binder["<F3>"] = "search\n"
binder["<Alt-F3>"] = "search(backward=True)\n"
binder["<Control-f>"] = "search "
