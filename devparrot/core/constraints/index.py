
from picoparse import string

from picoparse import one_of, many, many1, run_parser, optional
from picoparse import choice, any_token, satisfies
from picoparse import NoMatch
from picoparse.text import quoted
from picoparse import partial, tri, commit, fail, eof

from devparrot.core.utils.posrange import *

_reserved_kw = {'insert', 'i', 'current', 'c', 'start', 'end', 's', 'sel', 'selection', 'all', 'ws', 'we', 'ls', 'le', 'line', 'word', 'first', 'last'}

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
	what = choice( sinteger, lambda : u''.join(string("first")), lambda:u''.join(string("last")) )
	return lambda index : RangePos(index, what)

@tri
def rangeEndModifier(default, markSet, tagSet):
	idx = something(default, markSet, tagSet)
	if not idx.is_index:
		fail()
	return lambda base: StartEndRange(base, idx)

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




