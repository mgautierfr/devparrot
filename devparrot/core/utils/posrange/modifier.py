
import Tkinter
from range import Range
from devparrot.core import mimemapper

class StartEndRange(object):
    is_index = False
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def resolve(self, model):
        return Range(self.start.resolve(model), self.end.resolve(model))

    def __eq__(self, other):
        return (self.__class__, self.start, self.end) == (other.__class__, other.start, other.end)

    def __str__(self):
        return "<RANGE %s %s>"%(self.start, self.end)

class Line(object):
    is_index = False
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        try:
            idx = model.index("%d.0"%self.index)
        except TypeError:
            idx = self.index.resolve(model)
        return Range(model.linestart(idx), model.lineend(idx))

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<LINE %s>"%(self.index)

class Word(object):
    is_index = False
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        idx = self.index.resolve(model)
        return Range(model.index("%s wordstart"%str(idx)), model.index("%s wordend"%str(idx)))

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

class CharDelta(object):
    is_index = True
    def __init__(self, index, number):
        self.index = index
        self.number = number

    def resolve(self, model):
        idx = self.index.resolve(model)
        return model.addchar(idx, self.number)

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<CHARDELTA %s %d>"%(self.index, self.number)

class LineDelta(object):
    is_index = True
    def __init__(self, index, number):
        self.index = index
        self.number = number

    def resolve(self, model):
        idx = self.index.resolve(model)
        return model.addline(idx, self.number)

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<LINEDELTA %s %d>"%(self.index, self.number)

class WordStart(object):
    is_index = True
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        from devparrot.core import session
        start_search = self.index.resolve(model)
        mimetype = mimemapper.mimeMap.get(str(model.document.get_mimetype()))
        regex = u"[%(wchars)s]+[^%(wchars)s]*"%{'wchars':session.config.wchars.get(mimetype)}
        match_start = Tkinter.Text.search(model, regex, str(start_search), regexp=True, backwards=True)
        return model.index(match_start)

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<WORDSTART %s>"%(self.index)

class WordEnd(object):
    is_index = True
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        from devparrot.core import session
        start_search = self.index.resolve(model)
        mimetype = mimemapper.mimeMap.get(str(model.document.get_mimetype()))
        regex = u"[^%(wchars)s]*[%(wchars)s]+"%{'wchars':session.config.wchars.get(mimetype)}
        count = Tkinter.IntVar()
        match_start = Tkinter.Text.search(model, regex, str(start_search), regexp=True, count=count)
        return model.index("%s + %d c"%(match_start, count.get()))
    
    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<WORDEND %s>"%(self.index)

class LineStart(object):
    is_index = True
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        idx = self.index.resolve(model)
        return model.linestart(idx)

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<LINESTART %s>"%(self.index)

class LineEnd(object):
    is_index = True
    def __init__(self, index):
        self.index = index

    def resolve(self, model):
        idx = self.index.resolve(model)
        return model.lineend(idx)

    def __eq__(self, other):
        return (self.__class__, self.index) == (other.__class__, other.index)

    def __str__(self):
        return "<LINEEND %s>"%(self.index)

class RangePos(object):
    is_index = True
    def __init__(self, range, pos):
        self.range = range
        self.pos = pos

    def resolve(self, model):
        rang = self.range.resolve(model)
        if self.pos in ("first", 0):
            return rang.first
        if self.pos == "last":
            return rang.last
        if self.pos > 0:
            return model.addchar(rang.first, self.pos)
        else:
            return model.delchar(rang.last, -self.pos)

    def __eq__(self, other):
        return (self.__class__, self.range, self.pos) == (other.__class__, other.range, other.pos)

    def __str__(self):
        return "<RANGEPOS %s %s>"%(self.range, self.pos)

class RegexRange(object):
    is_index = False
    def __init__(self, index, forward, regex):
        self.index = index
        self.forward = forward
        self.regex = regex

    def resolve(self, model):
        idx = self.index.resolve(model)
        start_search = "1.0"
        stop_search = "end"
        if self.index.is_index:
            if self.forward:
                start_search = "%s+1c"%str(idx)
            else:
                stop_search = str(idx)
        else:
            start_search = "%s+1c"%str(idx.first)
            stop_search = str(idx.last)
        get_search = 0 if self.forward else -1
        indices = list(model.search(self.regex, start_search, stop_search))
        return Range(*indices[get_search])

    def __eq__(self, other):
        return (self.__class__, self.index, self.forward, self.regex) == (other.__class__, other.index, other.forward, other.regex)

    def __str__(self):
        return "<REGEXRANGE %s %s %s>"%(self.index, self.forward, self.regex)

