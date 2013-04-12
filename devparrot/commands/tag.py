
from devparrot.core.command import MasterCommand, SubCommand
from devparrot.core import constraints
from devparrot.core import capi

class tag(MasterCommand):
    """ Tag help stuff"""

    @SubCommand(
    tagList = constraints.Stream()
    )
    def set(tagName, tagList):
        tgList = [ str(item) for tuple_ in tagList for item in tuple_]
        capi.currentDocument.model.tag_add(tagName, *tgList)



