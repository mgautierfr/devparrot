import os
from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi

@Command(
files = constraints.File(mode=(constraints.File.OPEN, constraints.File.NEW), help="a list of file to open")
)
def open(*files):
    """
    Open a existing or new file
    """
    for fileToOpen in files:
        open_a_file(fileToOpen)

def open_a_file(fileToOpen):
    if not fileToOpen: return False
    lineToGo = 1
    # if path doesn't exist and we have a line marker, lets go to that line
    if not os.path.exists(fileToOpen):
        parts = fileToOpen.split(':')
        if len(parts) == 2:
            fileToOpen = parts[0]
            try :
                lineToGo = int(parts[1])
            except ValueError:
                pass
    if capi.file_is_opened(fileToOpen):
        doc = capi.get_file(fileToOpen)
    else:
        from devparrot.core.document import Document
        from devparrot.documents.fileDocSource import FileDocSource
        doc = Document(FileDocSource(fileToOpen))
        capi.add_file(doc)
        doc.load()
    capi.currentDocument = doc
    doc.goto_index("%s.0"%lineToGo)


binder["<Control-o>"] = "open\n"
