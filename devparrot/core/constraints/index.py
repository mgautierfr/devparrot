
from picoparse import string

from picoparse import one_of, many, many1, run_parser, optional
from picoparse import choice, any_token, satisfies
from picoparse import NoMatch
from picoparse.text import quoted
from picoparse import partial, tri, commit, fail, eof

from devparrot.core.errors import BadArgument

class Mark(object):
	is_index = True
	_reduced = {"i":"insert", "c":"current"}
	def __init__(self, markName):
		self.markName = self._reduced.get(markName, markName)

	def resolve(self, model):
		if self.markName == "start":
			return model.index("1.0")
		return model.index(self.markName)

	def __eq__(self, other):
		return (self.__class__, self.markName) == (other.__class__, other.markName)

	def __str__(self):
		return "<MARK %s>"%self.markName

class Range(object):
	is_index = False
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def resolve(self, model):
		return self.start.resolve(model), self.end.resolve(model)

	def __eq__(self, other):
		return (self.__class__, self.start, self.end) == (other.__class__, other.start, other.end)

	def __str__(self):
		return "<RANGE %s %s>"%(self.start, self.end)

class Tag(object):
	is_index = False
	_reduced = {"s":"sel", "selection":"sel"}
	def __init__(self, tagName):
		self.tagName = self._reduced.get(tagName, tagName)

	def resolve(self, model):
		if self.tagName == "all":
			return model.index("1.0") , model.index("end")
		try:
		    return model.index("%s.first"%self.tagName) , model.index("%s.last"%self.tagName)
		except BadArgument:
		    if self.tagName == "sel":
		        idx = model.index("insert")
		        return (idx, idx)

	def __eq__(self, other):
		return (self.__class__, self.tagName) == (other.__class__, other.tagName)

	def __str__(self):
		return "<TAG %s>"%self.tagName

class Line(object):
	is_index = False
	def __init__(self, index):
		self.index = index

	def resolve(self, model):
		try:
			idx = "%d.0"%self.index
		except TypeError:
			idx = self.index.resolve(model)
		return model.index("%s linestart"%str(idx)), model.index("%s lineend"%str(idx))

	def __eq__(self, other):
		return (self.__class__, self.index) == (other.__class__, other.index)

	def __str__(self):
		return "<LINE %s>"%(self.index)

class Word(object):
	is_index = False
	def __init__(self, index):
		self.index = index

	def resolve(self, model):
		try:
			idx = "%d.0"%self.index
		except TypeError:
			idx = self.index.resolve(model)
		return model.index("%s wordstart"%str(idx)), model.index("%s wordend"%str(idx))

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
		idx = self.index.resolve(model)
		return model.index("%s wordstart"%str(idx))

	def __eq__(self, other):
		return (self.__class__, self.index) == (other.__class__, other.index)

	def __str__(self):
		return "<WORDSTART %s>"%(self.index)

class WordEnd(object):
	is_index = True
	def __init__(self, index):
		self.index = index

	def resolve(self, model):
		idx = self.index.resolve(model)
		return model.index("%s wordend"%str(idx))

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
		start, end = self.range.resolve(model)
		if self.pos in ("start", 0):
			return start
		if self.pos == "end":
			return end
		if self.pos > 0:
			return model.index("%s + %d c"%(start, self.pos))
		else:
			return model.index("%s - %d c"%(end, -self.pos))

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
		end_search = "end"
		if self.index.is_index:
			if self.forward:
				start_search = "%s+1c"%str(idx)
			else:
				stop_search = str(idx)
		else:
			start_search = "%s+1c"%str(idx[0])
			stop_search = str(idx[1])
		get_search = 0 if self.forward else -1
		indices = list(model.search(self.regex, start_search, stop_search))
		return indices[get_search]

	def __eq__(self, other):
		return (self.__class__, self.index, self.forward, self.regex) == (other.__class__, other.index, other.forward, other.regex)

	def __str__(self):
		return "<REGEXRANGE %s %s %s>"%(self.index, self.forward, self.regex)

_reserved_kw = {'insert', 'i', 'current', 'c', 'start', 'end', 's', 'sel', 'selection', 'all', 'ws', 'we', 'ls', 'le', 'line', 'word'}

@tri
def identifier_char1():
    def test(l):
        if not l:
            return False
        return l.isalpha() or l in "_"
    return satisfies(test)

@tri
def identifier_char():
    def test(l):
        if not l:
            return False
        return l.isalpha() or l.isdigit() or l in "_"
    return satisfies(test)

@tri
def identifier():
	first = identifier_char1()
	rest = many(identifier_char)
	ident = ''.join([first] + rest)
	if ident in  _reserved_kw:
		fail()
	return ident

def integer():
	return int(u''.join(many1(partial(one_of, "0123456789"))))

def sinteger():
	signe = optional( partial(one_of, "-+"), "+")
	int_ = integer()
	if signe == "-":
		return -int_
	return int_


def string_char():
    char = any_token()
    if char == '\\':
        char = any_token()
    return char

def string_literal():
	return partial( quoted, string_char)

@tri
def userMark(markSet):
	mark = identifier()
	if mark not in markSet:
		fail()
	return mark

@tri
def mark(markSet):
	l = [ lambda i=i: u''.join(string(i)) for i in ("insert", "i", "current", "c", "start", "end")]
	l.append( partial(userMark, markSet) )
	markName = choice(*l)
	return Mark( markName )

@tri
def userTag(tagSet):
	tag = identifier()
	if tag not in tagSet:
		fail()
	return tag

@tri
def tag(tagSet):
	l = [ lambda i=i: u''.join(string(i)) for i in ("selection", "sel", "s", "all")]
	l.append( partial(userTag, tagSet) )
	tagName = choice(*l)
	return Tag( tagName )

def line():
	return Line(integer())

@tri
def charDelta():
	value = sinteger()
	string("c")
	return lambda index: CharDelta(index, value)

@tri
def lineDelta():
	value = sinteger()
	string("l")
	return lambda index: LineDelta(index, value)

indexModifiers_ = {
"ws" : WordStart,
"we" : WordEnd,
"ls" : LineStart,
"le" : LineEnd
}

@tri
def directIndexModifier():
	what = u''.join(choice( *[partial(string, i) for i in indexModifiers_.keys() ]))
	return lambda index, t=indexModifiers_[what] : t(index)


rangeModifiers_ = {
"line" : Line,
"word" : Word,
}

@tri
def directRangeModifier():
	what = u''.join(choice( *[partial(string, i) for i in rangeModifiers_.keys() ]))
	return lambda index, t=rangeModifiers_[what] : t(index)

def regexModifier(direction):
	regex = quoted()
	return lambda index : RegexRange(index, direction, regex)

def rangePos():
	what = choice( sinteger, lambda : u''.join(string("start")), lambda:u''.join(string("end")) )
	return lambda index : RangePos(index, what)

@tri
def rangeEndModifier(default, markSet, tagSet):
	idx = something(default, markSet, tagSet)
	if not idx.is_index:
		fail()
	return lambda base: Range(base, idx)

# modifier applied to a index
def index_modifier(base, markSet, tagSet):
	modifier =  optional( partial( choice, charDelta, lineDelta), None)
	if modifier is None:
		sep = one_of(":~?/")
		if sep == ":":
			modifier = choice( directRangeModifier, partial(rangeEndModifier, lambda:base, markSet, tagSet))
		elif sep == "~":
			modifier = directIndexModifier()
		else:
			modifier = regexModifier(sep=="/")
	return modifier
	
# modifier applied to a range
def range_modifier(markSet, tagSet):
	sep = one_of(".?/")
	if sep == ".":
		modifier = rangePos()
	else:
		modifier = regexModifier(sep=="/")
	return modifier

def something(default, markSet, tagSet):
	# try base
	base = optional( partial( choice, partial(mark, markSet), partial(tag, tagSet), line), None)
	if base is None:
		base = default()
	non_local = {'base':base}

	def inner():
		if non_local['base'].is_index:
			modifier = index_modifier(non_local['base'], markSet, tagSet)
		else:
			# range to index ?
			modifier = range_modifier(markSet, tagSet)
		non_local['base'] = modifier(non_local['base'])

	many(inner)
	eof()
	return non_local['base']

def parse_something(text, markSet, tagSet):
	ret, left = run_parser(partial(something, lambda:Mark("insert"), markSet, tagSet), text)
	return ret




