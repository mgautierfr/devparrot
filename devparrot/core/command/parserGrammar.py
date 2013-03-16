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

from picoparse import string

from picoparse import one_of, many, many1, many_until, not_one_of, run_parser, optional
from picoparse import choice, peek, eof, any_token, satisfies, not_followed_by
from picoparse import sep, sep1, NoMatch
from picoparse.text import quote, whitespace, whitespace1
from picoparse import partial, tri, commit, fail

from tokens import *

def index():
    import picoparse
    return picoparse.local_ps.value.index

@tri
def pipe_sep():
    whitespace()
    string('|')
    return '|'

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
        return l.isalpha() or l.isdigit() or l in "_."
    return satisfies(test)

@tri
def digit():
    return satisfies(lambda l: l and l.isdigit())

@tri
def optspecial(name):
    whitespace()
    ret = optional(partial(string,name), None)
    return ret is not None

@tri
def special(name):
    whitespace()
    return string(name)

@tri
def number():
    whitespace()
    idx = index()
    lead = ''.join(many1(digit))
    if optional(partial(one_of, '.'), None):
        trail = ''.join(many1(digit))
        return Number(index=idx, len=index()-idx, value=float(lead + '.' + trail))
    else:
        return Number(index=idx, len=index()-idx, value=int(lead))

@tri
def string_char(quote):
    char = not_one_of(quote)
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string_char1():
    char = not_one_of(" ,()[]{}|")
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string_char(nokeyword):
    if nokeyword:
        char = not_one_of(" ()[]{}|=")
    else:
        char = not_one_of(" ()[]{}|")
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string(nokeyword):
    idx = index()
    first = unquoted_string_char1()
    rest = many(partial(unquoted_string_char, nokeyword))
    if nokeyword:
        not_followed_by(partial(one_of, "="))
    st = ''.join([first] + rest)
    closed = optional(whitespace1, None)
    return UnquotedString(index=idx, len=index()-idx, values=st, closed=(closed is not None))
    
@tri
def string_literal():
    whitespace()
    idx = index()
    quote = optional(partial(one_of,'\'"'), None)
    if quote:
        st = ''.join(many(partial(string_char, quote)))
        if quote == "'":
            return SimpleString(index=idx, len=index()-idx, values=st, closed=optspecial(quote))
        else:
            return DoubleString(index=idx, len=index()-idx, values=st, closed=optspecial(quote))
    return partial(unquoted_string, True)()

@tri
def identifier1():
    whitespace()
    idx = index()
    first = identifier_char1()
    rest = many(identifier_char)
    name = ''.join([first] + rest)
    return Identifier(index=idx, len=index()-idx, name=name)

@tri
def identifier():
    idt = identifier1()
    not_followed_by(partial(one_of, "/\\="))
    return idt
    
@tri
def list_():
    whitespace()
    idx = index()
    special('(')
    st = ''.join(many(partial(string_char, ')')))
    closed=optspecial(')')
    return List(index=idx, len=index()-idx, values=st, closed=closed )
    
@tri
def keywordparameter():
    whitespace()
    idx = index()
    name = identifier1()
    whitespace()
    special("=")
    whitespace()
    value = optional( partial (choice, parameter, partial( unquoted_string, False) ), "")
    return KeywordArg(index=idx, len=index()-idx, name=name, value=value)

@tri
def argument_sep():
    return whitespace1()

@tri
def parameter():
    return choice(identifier, number, list_, string_literal)

@tri
def keywordparameter_list():
    whitespace()
    l = sep( keywordparameter, argument_sep )
    return l

@tri
def keywordparameter_list1():
    argument_sep()
    l = keywordparameter_list()
    return l

@tri
def argument_list_nokw():
    whitespace()
    l1 = sep1( parameter, argument_sep )
    sep = optional(argument_sep, None)
    if sep is None:
        fail()
    not_followed_by(keywordparameter)
    return l1 + [New(index=index())]

@tri
def argument_list1():
    whitespace()
    l1 = sep1( parameter, argument_sep )
    l2 = optional( keywordparameter_list1, [])
    return l1+l2

@tri
def argument_list():
    return optional( partial( choice, argument_list_nokw,
                                      argument_list1,
                                      keywordparameter_list), [])

@tri
def commandCall():
    whitespace()
    ident = identifier()
    wp = choice(whitespace1, eof)
    if not wp:
        return ident

    parameter = argument_list()

    if not parameter:
        parameter = [New(index=index())]
    return CommandCall(index=ident.index, len=index()-ident.index, name=ident.name, values=parameter, closed=True)

@tri
def userCommand():
    c = sep1( commandCall, pipe_sep )
    
    pipe = Pipe(index=c[0].index, len=index()-c[0].index, values=c)
    eof()
    return pipe


def parse_input_text(text):
    if not text:
        return New(index=0)
    try:
        ret, _ = run_parser(userCommand, text)
        return ret
    except NoMatch:
        print "Can't parse |%s|"%text
        return None

def rewrite_command(text):
    token = parse_input_text(text)
    if not token:
        return None
    last = token.values[-1]
    if last.get_type() == 'Identifier':
        last = CommandCall(index=last.index, len=len(text), name=last.name, values=[New(index=len(text))], closed=True)
        token.values[-1] = last
    return token.rewrited()
