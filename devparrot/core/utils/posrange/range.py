from devparrot.core.errors import *

class Range:
    def __init__(self, textWidget, startIndex, endIndex):
        if startIndex > endIndex:
            raise BadArgument("{} is superior to {}".format(startIndex, endIndex))
        self.textWidget = textWidget
        self.startIndex = startIndex
        self.endIndex = endIndex

    def __str__(self):
        return "%s:%s" % (str(self.startIndex), str(self.endIndex))
    
    def __repr__(self):
        return "<Range instance pos %s [%s:%s]>" % (self.textWidget, str(self.startIndex), str(self.endIndex))

    def get_content(self):
        return self.textWidget.get(str(self.startIndex), str(self.endIndex))
