from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

class search(Command):
    lastSearch = None
    Command.add_alias("bsearch", "search backward", 1)
    searchText = constraints.Default(default=lambda : search.lastSearch)
    backward = constraints.Boolean(true=("backward"), false=("forward"), default=lambda : False)
    def run(cls, backward, searchText):
        cls.lastSearch = searchText
        if searchText:
            return capi.currentDocument.search(backward, searchText)

binder["<F3>"] = "search\n"
binder["<Alt-F3>"] = "bsearch\n"
binder["<Control-f>"] = "search "
