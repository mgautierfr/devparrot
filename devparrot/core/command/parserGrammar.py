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

_escaped = "nt\\"
_special_escaped = {'n':'\n', 't':'\t'}
@tri
def quoted_string_char(quote):
    char = not_one_of(quote)
    if char == '\\':
        char = optional(partial(one_of, _escaped+quote), '\\')
        char = _special_escaped.get(char, char)
    return char

_always_excluded = " |\n=,"
# " ,()[]{}|%\n"
@tri
def unquoted_string_char1(excluded):
	return not_one_of(_always_excluded+excluded+"%")

@tri
# " ,()[]{}|\n="
def unquoted_string_char(excluded):
    return not_one_of(_always_excluded+excluded)

@tri
def unquoted_string(excluded):
    idx = index()
    first = unquoted_string_char1(excluded)
    rest = many(partial(unquoted_string_char, excluded))
    #if there is a '=' this is not a string but a identifier => fail.
    not_followed_by(partial(one_of, "="))
    st = ''.join([first] + rest)
    end = index()
    closed = optional(eof, False)
    return UnquotedString(index=idx, len=end-idx, values=st, closed=(closed is not None))
    
@tri
def string_literal(excluded):
    whitespace()
    idx = index()
    quote = optional(partial(one_of,'\'"'), None)
    if quote:
        st = ''.join(many(partial(quoted_string_char, quote)))
        closed=optspecial(quote)
        if quote == "'":
            return SimpleString(index=idx, len=index()-idx, values=st, closed=closed)
        else:
            return DoubleString(index=idx, len=index()-idx, values=st, closed=closed)
    return unquoted_string(excluded)

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
def list_(excluded):
    whitespace()
    idx = index()
    special('[')
    st = many(partial(string_literal, excluded+'[]'))
    closed=optspecial(']')
    return List(index=idx, len=index()-idx, values=st, closed=closed )
    
@tri
def keywordparameter(excluded):
    whitespace()
    idx = index()
    name = identifier1()
    whitespace()
    special("=")
    whitespace()
    value = optional( partial(parameter, excluded), "")
    return KeywordArg(index=idx, len=index()-idx, name=name, value=value)

@tri
def parameter(excluded):
    return choice(partial(list_, excluded), partial(string_literal, excluded), partial(macroCall, excluded))

@tri
def argument_list(separator, excluded):
    whitespace()
    l1 = optional( partial(sep1, partial(parameter, excluded), separator), [])
    if l1:
        sep = optional( separator, None)
        if sep is None:
            return l1

    l2 = optional( partial(sep1, partial(keywordparameter, excluded), separator), [New(index=index())])
    return l1+l2


@tri
def macroCall(excluded):
    whitespace()
    idx = index()
    special('%')
    expanded = optspecial('%')
    ident = optional( identifier, None)

    if ident is None:
        return MacroCall(index=idx, len=index()-idx, name="", values=[], opened=False, closed=False, expanded=expanded)

    parameter = []
    closed = False
    opened = optspecial('(')
    if opened:
        parameter = argument_list(partial(special, ','), excluded+")")
        closed = optspecial(')')
        if not parameter and not closed:
            parameter = [New(index=index())]
        if parameter and closed and parameter[-1].get_type() == "New":
            del parameter[-1]
    return MacroCall(index=idx, len=index()-idx, name=ident.name, values=parameter, opened=opened, closed=closed, expanded=expanded)

@tri
def commandCall():
    whitespace()
    ident = identifier()
    wp = choice(whitespace1, eof)
    if not wp:
        return ident

    parameter = argument_list(whitespace1, "")

    if not parameter:
        parameter = [New(index=index())]
    return CommandCall(index=ident.index, len=index()-ident.index, name=ident.name, values=parameter, closed=False)

@tri
def userCommand():
    def inner():
        sep = choice(partial(special, "\n"), pipe_sep)
        if sep:
            commands[-1].closed = True
        if sep == "\n":
            commands.append("\n")
        whitespace()
        command = optional(commandCall, None)
        commands.append(command)

    commands = [ commandCall() ]
    many(inner)
    
    pipe = Pipe(index=commands[0].index, len=index()-commands[0].index, values=commands)
    eof()
    return pipe


def parse_input_text(text, forCompletion=True):
    from devparrot.core import session
    from devparrot.core.errors import InvalidSyntax
   # import pdb; pdb.set_trace()
    session.logger.debug("parsing %s", repr(text))
    if not text.strip():
        return Pipe(index=0, len=len(text), values=[New(index=len(text))])
    try:
        ret, _ = run_parser(userCommand, text)
        if forCompletion:
            lastCommand = ret.values[-1]
            if lastCommand is None:
                ret.values[-1] = New(index=len(text))
        else:
            lastCommand = ret.values[-1]
            if lastCommand is None:
                 raise InvalidSyntax("Can't parse %s", text)
            if lastCommand.get_type() == "Identifier":
                ret.values[-1] = CommandCall(index=lastCommand.index, len=lastCommand.len, name=lastCommand.name, values=[], closed=False)
        return ret
    except NoMatch:
        raise InvalidSyntax("Can't parse %s", text)
