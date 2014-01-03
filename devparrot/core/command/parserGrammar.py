#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
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
#    Copyright 2011-2013 Matthieu Gautier


from picoparse import string

from picoparse import one_of, many, many1, many_until, not_one_of, run_parser, optional
from picoparse import choice, peek, eof, is_eof, any_token, satisfies, not_followed_by
from picoparse import sep, sep1, NoMatch
from picoparse.text import quote
from picoparse import partial, tri, commit, fail

from tokens import *


whitespace_char = partial(one_of, " \t")
whitespace = partial(many, whitespace_char)
whitespace1 = partial(many1, whitespace_char)

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
def optspecial(name):
    whitespace()
    ret = optional(partial(string,name), None)
    return ret is not None

@tri
def special(name):
    whitespace()
    string(name)
    return name

@tri
def string_char(quote):
    char = not_one_of(quote)
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string_char1():
    char = not_one_of(" ,()[]{}|%\n")
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string_char():
    char = not_one_of(" ,()[]{}|\n=")
    if char == '\\':
        char = optional(any_token, '\\')
    return char

@tri
def unquoted_string():
    idx = index()
    first = unquoted_string_char1()
    rest = many(unquoted_string_char)
    not_followed_by(partial(one_of, "="))
    st = ''.join([first] + rest)
    end = index()
    closed = optional(eof, False)
    return UnquotedString(index=idx, len=end-idx, values=st, closed=(closed is not None))
    
@tri
def string_literal():
    whitespace()
    idx = index()
    quote = optional(partial(one_of,'\'"'), None)
    if quote:
        st = ''.join(many(partial(string_char, quote)))
        closed=optspecial(quote)
        if quote == "'":
            return SimpleString(index=idx, len=index()-idx, values=st, closed=closed)
        else:
            return DoubleString(index=idx, len=index()-idx, values=st, closed=closed)
    return unquoted_string()

@tri
def identifier1():
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
    special('[')
    st = many(string_literal)
    closed=optspecial(']')
    return List(index=idx, len=index()-idx, values=st, closed=closed )
    
@tri
def keywordparameter():
    whitespace()
    idx = index()
    name = identifier1()
    whitespace()
    special("=")
    whitespace()
    value = optional( parameter, "")
    return KeywordArg(index=idx, len=index()-idx, name=name, value=value)

@tri
def parameter():
    return choice(list_, string_literal, macroCall)

@tri
def argument_list(separator):
    whitespace()
    l1 = optional( partial(sep1, parameter, separator), [])
    if l1:
        sep = optional( separator, None)
        if sep is None:
            return l1

    l2 = optional( partial(sep1, keywordparameter, separator), [New(index=index())])
    return l1+l2


@tri
def macroCall():
    whitespace()
    idx = index()
    special('%')
    ident = optional( identifier, None)

    if ident is None:
        return MacroCall(index=idx, len=index()-idx, name="", values=[], opened=False, closed=False)

    parameter = []
    closed = False
    opened = optspecial('(')
    if opened:
        parameter = argument_list(partial(special, ','))
        closed = optspecial(')')
        if not parameter and not closed:
            parameter = [New(index=index())]
        if parameter and closed and parameter[-1].get_type() == "New":
            del parameter[-1]
    return MacroCall(index=idx, len=index()-idx, name=ident.name, values=parameter, opened=opened, closed=closed)

@tri
def commandCall():
    whitespace()
    ident = identifier()
    wp = choice(whitespace1, eof)
    if not wp:
        return ident

    parameter = argument_list(whitespace1)

    if not parameter:
        parameter = [New(index=index())]
    return CommandCall(index=ident.index, len=index()-ident.index, name=ident.name, values=parameter, closed=False)

@tri
def userCommand():
    commands = [ commandCall() ]
    def inner():
        sep = choice(partial(special, "\n"), pipe_sep)
        if sep:
            commands[-1].closed = True
        if sep == "\n":
            commands.append("\n")
        commands.append(commandCall())

    many(inner)
    
    pipe = Pipe(index=commands[0].index, len=index()-commands[0].index, values=commands)
    eof()
    return pipe


def parse_input_text(text, forCompletion=True):
    from devparrot.core import session
    from devparrot.core.errors import InvalidSyntax
   # import pdb; pdb.set_trace()
    session.logger.debug("parsing %s", repr(text))
    if not text:
        return New(index=0)
    try:
        ret, _ = run_parser(userCommand, text)
        if not forCompletion:
            lastCommand = ret.values[-1]
            if lastCommand.get_type() == "Identifier":
                ret.values[-1] = CommandCall(index=lastCommand.index, len=lastCommand.len, name=lastCommand.name, values=[], closed=False)
        return ret
    except NoMatch:
        raise InvalidSyntax("Can't parse %s", text)
