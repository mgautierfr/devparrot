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
def comma_sep():
    whitespace()
    string(",")
    return ","

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
    char = not_one_of(" ,()[]{}")
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string_char(nokeyword):
    if nokeyword:
        char = not_one_of(" ()[]{}=")
    else:
        char = not_one_of(" ()[]{}")
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
    return UnquotedString(index=idx, len=index()-idx, values=st)
    
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
def sep_parameter_list():
    whitespace()
    l = sep( partial(parameter, True), comma_sep )
    def inner():
        comma_sep()
        return [New(index=index())]
    return l + optional(inner, [])
    
@tri
def list_():
    whitespace()
    idx = index()
    special('[')
    l = sep_parameter_list()
    whitespace()
    closed=optspecial(']')
    if not l and not closed:
        l = [New(index=index())]
    return List(index=idx, len=index()-idx, values=l, closed=closed )
    
@tri
def keywordparameter():
    whitespace()
    idx = index()
    name = identifier1()
    whitespace()
    special("=")
    whitespace()
    value = optional( partial (choice, partial(parameter, True), partial( unquoted_string, False) ), "")
    return KeywordArg(index=idx, len=index()-idx, name=name, value=value)

@tri
def argument_sep(simple):
    if simple:
        return whitespace1()
    else:
        return comma_sep()

@tri
def parameter(simple):
    if simple:
        return choice(fullCommandCall, identifier, number, list_, string_literal)
    else:   
        return choice(commandCall, identifier, number, list_, string_literal)

@tri
def keywordparameter_list(simple):
    whitespace()
    l = sep( keywordparameter, partial( argument_sep, simple) )
    return l

@tri
def keywordparameter_list1(simple):
    partial (argument_sep, simple)()
    l = partial(keywordparameter_list, simple)()
    return l

@tri
def argument_list_nokw(simple):
    whitespace()
    l1 = sep1( partial(parameter, simple), partial( argument_sep, simple) )
    sep = optional(partial( argument_sep, simple), None)
    if sep is None:
        fail()
    not_followed_by(keywordparameter)
    return l1 + [New(index=index())]

@tri
def argument_list1(simple):
    whitespace()
    l1 = sep1( partial(parameter, simple), partial( argument_sep, simple) )
    l2 = optional( partial(keywordparameter_list1, simple) , [])
    return l1+l2

@tri
def argument_list(simple):
    return optional( partial( choice, partial(argument_list_nokw, simple),
                                      partial(argument_list1, simple),
                                      partial(keywordparameter_list, simple)), [])

@tri
def identifier_to_commandCall(simple, identifier):
    if simple:
        wp = choice(whitespace1, eof)
        if not wp:
            return identifier
    else:
        whitespace()
        special('(')

    parameter = partial(argument_list, simple)()

    closed = optspecial(')')
    if not parameter and not closed:
        parameter = [New(index=index())]
    return CommandCall(index=identifier.index, len=index()-identifier.index, name=identifier.name, values=parameter, closed=closed)

identifier_to_fullCommandCall = partial(identifier_to_commandCall, False)
identifier_to_simplifiedCommandCall = partial(identifier_to_commandCall, True)

@tri
def commandCall():
    return choice(fullCommandCall, simpleCommandCall)

@tri
def fullCommandCall():
    whitespace()
    v = identifier()
    return identifier_to_fullCommandCall(v)

@tri
def simpleCommandCall():
    whitespace()
    v = identifier()
    return identifier_to_simplifiedCommandCall(v)

@tri
def userCommand():
    c = commandCall()
    eof()
    return c


def parse_input_text(text):
    if not text:
        return New(0), ""
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
    if token.get_type() == 'Identifier':
        token = CommandCall(index=token.index, len=len(text), name=token.name, values=[New(index=len(text))], closed=False)
    return token.rewrited()
