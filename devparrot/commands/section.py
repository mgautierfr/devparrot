from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi
from devparrot.core.utils.posrange import Index

@Command(
startIndex = constraints.Index(),
endIndex = constraints.Index(),
content = constraints.Stream()
)
def section(startIndex, endIndex, content):
    """
    represent a section of the current document starting from startIndex and ending at endIndex.

    the section use as stream sink or stream source. (but not both)
    """
    model = capi.currentDocument.get_model()
    startIndex = Index(model, startIndex)
    endIndex = Index(model, endIndex)
    
    insertionMode = False

    for line in content:
        if not insertionMode:
            insertionMode = True
            model.delete(str(startIndex), str(endIndex))
            model.mark_set("dp::section_insert", str(startIndex))
            model.mark_gravity("dp::section_insert", 'right')
        model.insert("dp::section_insert", line)

    if insertionMode:
        model.mark_unset("dp::section_insert")
        # If we've got insertion do not make stream
        return None

    def gen():
        if startIndex.line == endIndex.line:
            yield model.get(str(startIndex), str(endIndex))
        else:
            yield model.get(str(startIndex), "%s lineend"%str(startIndex))
            for i in range(startIndex.line+1, endIndex.line):
                yield model.get("%d.0"%i, "%d.0 lineend"%i)
            yield model.get("%s linestart"%str(endIndex), str(endIndex))

    return gen()