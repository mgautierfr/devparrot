import os
from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints
from devparrot.core import capi

class open(Command):
    files = constraints.File(mode=(constraints.File.OPEN, constraints.File.NEW), multiple=True)
    def open_a_file(cls, fileToOpen):
        if not fileToOpen: return False
        lineToGo = None
        # if path doesn't exist and we have a line marker, lets go to that line
        if not os.path.exists(fileToOpen):
            parts = fileToOpen.split(':')
            if len(parts) == 2:
                fileToOpen = parts[0]
                try :
                    lineToGo= int(parts[1])
                except: pass
        if capi.file_is_opened(fileToOpen):
            doc = capi.get_file(fileToOpen)
        else:
            from devparrot.core.document import Document
            from devparrot.documents.fileDocSource import FileDocSource
            doc = Document(FileDocSource(fileToOpen))
            capi.add_file(doc)
            doc.load()
        capi.currentDocument = doc
        if lineToGo:
            doc.goto_index("%s.0"%lineToGo-1)
        return True

    def run(cls, files, *args):
        ret = True
        for fileToOpen in files:
            ret = ret and cls.open_a_file(fileToOpen)
        return ret

