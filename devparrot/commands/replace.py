from devparrot.core.command import Command, Alias
from devparrot.core.constraints import Stream
from devparrot.core.commandLauncher import create_section
from devparrot.core import capi

class inner:
    @staticmethod
    def replace(pattern, repl, ranges):
        import re
        model = capi.currentDocument.model
        for start, stop in ranges:
            text = model.get(str(start), str(stop))
            new = re.sub(pattern, repl, text)
            model.replace(str(start), str(stop), new)

Command(
ranges=Stream()
)(inner.replace, create_section("capi"))


@Alias()
def replace(regex, subst):
    return "capi.search {0!r} | capi.replace {0!r} {1!r}".format(regex, subst) 
