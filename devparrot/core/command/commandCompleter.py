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


from devparrot.core.completion import Completion, CompletionSystem
from devparrot.core.errors import InvalidSyntax

class CommandCompletion(Completion):
    def __init__(self, *args, **kwords):
        Completion.__init__(self,*args, **kwords)

    def __str__(self):
        return "%s "%self.value

class MacroCompletion(Completion):
    def __init__(self, *args, **kwords):
        Completion.__init__(self, *args, **kwords)

    def __str__(self):
        return "%%%s("%self.value

class DoubleStringCompletion(Completion):
    def __init__(self, *args, **kwords):
        Completion.__init__(self,*args, **kwords)

    def __str__(self):
        template = '"%s"' if self.final else '"%s'
        return template % self.value.encode("utf8")


class SimpleStringCompletion(Completion):
    def __init__(self, *args, **kwords):
        Completion.__init__(self,*args, **kwords)

    def __str__(self):
        template = "'%s'" if self.final else "'%s"
        return template % self.value.encode("utf8")

def get_command(commandName):
    from devparrot.core import session
    if not commandName:
        return None
    return session.commands.get(commandName, None)

def get_macro(macroName):
    from devparrot.core import session
    if not macroName:
        return None
    return session.macros.get(macroName, None)

def _get_callCompletions(list_,  name, CompletionType):
    ret = []
    for command in list_:
        if command.startswith(name):
            ret.append(CompletionType(value=command, final=True))
    return ret

def get_commandCompletions(tokenName):
    from devparrot.core import session
    return _get_callCompletions(session.commands, tokenName, CommandCompletion)

def get_macroCompletions(tokenName):
    from devparrot.core import session
    return _get_callCompletions(session.macros, tokenName, MacroCompletion)

def get_argumentCompletions(callObject, argumentContainer):
    if callObject is None:
        return (0, [])

    for i, value in enumerate(argumentContainer.values[:-1]):
        callObject.provide_value(i, value)

    try:
        constraint = callObject.get_constraint(len(argumentContainer.values)-1)
    except IndexError:
        return (0, [])
    return constraint.complete_context(argumentContainer.values[-1])


    
def get_completions(text):
    from devparrot.core.command.parserGrammar import parse_input_text
    try:
        pipe = parse_input_text(text)
    except InvalidSyntax:
        return (None, [])

    last = pipe.values[-1]
    if last.get_type() == "Identifier":
        return (last.index, get_commandCompletions(last.name))

    if last.get_type() == "New":
        return (last.index, get_commandCompletions(""))
    
    if last.get_type() == 'CommandCall':
        try:
            lastArg = last
            try:
                while True:
                    if lastArg.values[-1].get_type() == 'MacroCall':
                        lastArg = lastArg.values[-1]
                    else:
                        break
            except IndexError:
                pass
            if lastArg.get_type() == 'MacroCall':
                if not lastArg.opened:
                    return (lastArg.index, get_macroCompletions(lastArg.name))
                else:
                    return get_argumentCompletions(get_macro(str(lastArg.name)), lastArg)
        except IndexError:
            pass

        return get_argumentCompletions(get_command(str(last.name)), last)
    return (None, [])

class ControlerEntryCompletion(CompletionSystem):
    def __init__(self, textWidget):
        CompletionSystem.__init__(self, textWidget)

    def get_completions(self, text):
        startIndex, completions = get_completions(text)
        if startIndex is None:
            startIndex = len(text)
        return "1.%d"%startIndex, completions

    def complete(self, startIndex, text):
        oldInsert = self.textWidget.index("insert")
        self.textWidget.tk.call((self.textWidget._w, 'replace', startIndex, 'insert', text))
        self.textWidget.tag_remove( 'sel', '1.0', 'end' )
        self.textWidget.mark_set( 'sel.first', oldInsert)
        self.textWidget.mark_set( 'sel.last', startIndex +"+%dc"%len(text))
        self.textWidget.tag_add( 'sel', oldInsert, startIndex +"+%dc"%len(text))
        
