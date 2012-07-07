#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

import pyparsing
import core
import os.path

OptionalQuotedString = lambda g:(pyparsing.Suppress('"')+g+pyparsing.Suppress('"'))^g

uinteger = pyparsing.Word(pyparsing.nums).setParseAction(lambda t:[int(t[0])])
integer = pyparsing.Word(pyparsing.nums+"-+", pyparsing.nums)
integer.setParseAction(lambda t:[int(t[0])])

path_elem = pyparsing.Word(pyparsing.srange("[a-zA-Z0-9_.]"))
path = pyparsing.Combine(pyparsing.Optional(pyparsing.Literal(".")*(1, 2) + "/") + pyparsing.delemitedList(path_elem, delim="/", combine=True))


def int2Doc(s, l, t):
	""" transform a integer to a doc"""
	index = int(t[0])
	document = core.controler.currentSession.get_documentManager().get_nthFile(index)
	if document is None:
		raise pyparsing.ParseException(s,l,"Wrong number")
	return [document]
def path2Doc(s, l, t):
	""" transform a path to a doc"""
	tok = os.path.abspath(t[0])
	if not core.controler.currentSession.get_documentManager().has_file(tok):
		raise pyparsing.ParseException(s, l, "Wrong name")
	return [core.controler.currentSession.get_documentManager().get_file(tok)]

def checkIndex(s, l, t):
	doc, indexstr = t
	import utils.annotations
	if doc is None:
		doc = core.controler.currentSession.get_currentDocument()
		if not doc:
			raise pyparsing.ParseException(s, l, "No doc given and no currentDoc")
	try:
		index = utils.annotations.Index(doc.get_model(), indexstr)
	except utils.annotations.BadArgument:
		raise pyparsing.ParseException(s, l, "Invalid value for index")
	return [index]

def checkRange(s, l, t):
	import utils.annotations
	doc, start, end = t
	if doc is None:
		doc = core.controler.currentSession.get_currentDocument()
		if not doc:
			raise pyparsing.ParseException(s, l, "No doc given and no currentDoc")
	try:
		start_ = utils.annotations.Index(doc.get_model(), start)
		end_ = utils.annotations.Index(doc.get_model(), end)
		range_ = utils.annotations.Range(doc.get_model(), start_, end_)
	except utils.annotations.BadArgument:
		raise pyparsing.ParseException(s, l, "Invalid value for range")
	return [range_]

def resolveRange(s, l, t):
	range_ = t[0]
	content = range_.get_content()
	return [content]

docindex = uinteger.copy()
docindex.addParseAction(int2Doc)

docpath = path.copy()
docpath.setParseAction(path2Doc)
doc = docindex | docpath




positional = pyparsing.Combine(uinteger + pyparsing.Optional("." + uinteger, default=".0"))
mark = ( pyparsing.Literal("insert")
       | pyparsing.Literal("current")
       | pyparsing.Literal("end")
       | pyparsing.Literal("i").setParseAction( pyparsing.replaceWith("insert") )
       | pyparsing.Literal("c").setParseAction( pyparsing.replaceWith("current") )
       | pyparsing.Literal("e").setParseAction( pyparsing.replaceWith("end") )
       )
mark = pyparsing.Optional(mark, default="insert")
tag = ( pyparsing.Literal("sel")
      | pyparsing.Literal("s").setParseAction( pyparsing.replaceWith("sel") )
      )
tagPositional = pyparsing.Combine(tag+"."+pyparsing.oneOf("first last"))
		
countedmodifierkw = ( pyparsing.Literal("chars")
                    | pyparsing.Literal("indices")
                    | pyparsing.Literal("lines")
                    | pyparsing.Literal("c").setParseAction( pyparsing.replaceWith("chars") )
                    | pyparsing.Literal("i").setParseAction( pyparsing.replaceWith("indices") )
                    | pyparsing.Literal("l").setParseAction( pyparsing.replaceWith("lines") )
                    )
countedmodifier = pyparsing.Combine( integer + countedmodifierkw , adjacent=False, joinString=" ")
directmodifier =  ( pyparsing.Literal("linestart")
                  | pyparsing.Literal("lineend")
                  | pyparsing.Literal("wordstart")
                  | pyparsing.Literal("wordend")
                  | pyparsing.Literal("ls").setParseAction( pyparsing.replaceWith("linestart") )
                  | pyparsing.Literal("le").setParseAction( pyparsing.replaceWith("lineend") )
                  | pyparsing.Literal("ws").setParseAction( pyparsing.replaceWith("wordstart") )
                  | pyparsing.Literal("we").setParseAction( pyparsing.replaceWith("wordend") )
                  )
modifier = pyparsing.ZeroOrMore(countedmodifier | directmodifier)
		
# ((mark ^ positional ^ tag) + modifier) will parse "1 chars" as 1.0 (+ error) instead of "insert + 1 chars"
# so split expression
positional_modifier = pyparsing.Combine(positional + modifier, adjacent=False, joinString=" ")
mark_modifier = pyparsing.Combine(mark + modifier, adjacent=False, joinString=" ")
tag_modifier = pyparsing.Combine(tagPositional + modifier, adjacent=False, joinString=" ")

index = pyparsing.Combine(mark_modifier ^ positional_modifier ^ tag_modifier, adjacent=False, joinString=" ")
index = OptionalQuotedString(index)
fullindex = pyparsing.Optional( doc + pyparsing.Suppress("@"), default=None ) + index
fullindex = OptionalQuotedString(fullindex)
fullindex.setParseAction(checkIndex)


indexRange = pyparsing.Optional( doc + pyparsing.Suppress("@"), default=None ) + index + pyparsing.Suppress(":") + index
indexRange = OptionalQuotedString(indexRange)
indexRange.setParseAction(checkRange)


rangeExpander = pyparsing.Suppress("[") + indexRange + pyparsing.Suppress("]")
rangeExpander.setParseAction(resolveRange)
_range = pyparsing.Combine(indexRange^tag, adjacent=False, joinString=" ")
