from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

class search(Command):
    lastSearch = None

    @staticmethod
    def regChecker(line):
        import re
        match = re.match(r"^/(.*)$", line)
        if match:
            return ("search", " ".join(match.groups()))
        match = re.match(r"^\?(.*)$", line)
        if match:
            return ("search backward ", " ".join(match.groups()))
        return None

    Command.add_expender(lambda line : search.regChecker(line))
    Command.add_alias("bsearch", "search backward", 1)
    searchText = constraints.Default(default=lambda : search.lastSearch)
    backward = constraints.Boolean(true=("backward"), false=("forward"), default=lambda : False)
    def run(cls, backward, searchText):
        cls.lastSearch = searchText
        if searchText:
            return capi.currentDocument.search(backward, searchText)


