from devparrot.capi import Command, Alias, create_section, get_currentDocument
from devparrot.capi import constraints
from devparrot.core.session import bindings

lastSearch = None
capi_section = create_section("capi")

class inner:
    @staticmethod
    def search(searchText):
        if not searchText:
            return None

        return get_currentDocument().model.search(searchText)

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
        "capi.search {0!r} | tag set search_tag".format(searchText),
        "goto {0!r}".format(searchChar+searchText)
    ]

    return "\n".join(commands)

@Alias()
def bsearch(searchText):
    return "search {0!r} backward=True".format(searchText)

bindings["<F3>"] = "search\n"
bindings["<Alt-F3>"] = "search backward=True\n"
bindings["<Control-f>"] = "search "
