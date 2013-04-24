from devparrot.capi import MasterCommand, SubCommand, get_currentDocument
from devparrot.capi.constraints import Stream

class tag(MasterCommand):
    """ Tag help stuff"""

    @SubCommand(
    tagList = Stream()
    )
    def set(tagName, tagList):
        tgList = [ str(item) for tuple_ in tagList for item in tuple_]
        get_currentDocument().model.tag_add(tagName, *tgList)



