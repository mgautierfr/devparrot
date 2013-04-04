from devparrot.core.command.baseCommand import Command
from devparrot.core.command.alias import Alias
from devparrot.core.command import constraints, binder
from devparrot.core.commandLauncher import create_section
from devparrot.core import capi

lastSearch = None
capi_section = create_section("capi")

class inner:
    @staticmethod
    def search(searchText):
        if not searchText:
            return None

        return capi.currentDocument.model.search(searchText)

Command(
    backward = constraints.Boolean(default=lambda : False)
)(inner.search, capi_section)


@Alias(
    searchText = constraints.Default(default=lambda : lastSearch),
    backward = constraints.Boolean(default=lambda :False)
)
def search(searchText, backward):
    """search for searchText in currentDocument
    """
    searchChar = "?" if backward else "/"

    global lastSearch
    lastSearch = searchText

    commands = [
        "capi.search %s | tag set search_tag"%searchText,
        "goto %s%s"%(searchChar, searchText)
    ]

    return "\n".join(commands)

@Alias()
def bsearch(searchText):
    return "search %s backward=True"%searchText

binder["<F3>"] = "search\n"
binder["<Alt-F3>"] = "search backward=True\n"
binder["<Control-f>"] = "search "
