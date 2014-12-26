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


from devparrot.core.completion import BaseCompletion, CompletionSystem
from devparrot.core.errors import InvalidSyntax

class CommandCompletion(BaseCompletion):
    def __init__(self, startIndex, name, already):
        BaseCompletion.__init__(self, startIndex=startIndex)
        self._name = name
        self.already = already

    def name(self):
        return self._name + " "

    def complete(self):
        return self._name[self.already:] + " "

    def final(self):
        return True

class MacroCompletion(BaseCompletion):
    def __init__(self, startIndex, name, already):
        BaseCompletion.__init__(self, startIndex=startIndex)
        self.n_ame = name
        self.already = already

    def name(self):
        return "%%%s("%self._name

    def complete(self):
        return self._name[self.already:] + "("

    def final(self):
        return True

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

def _get_callCompletions(list_, startIndex, name, CompletionType):
    ret = []
    for command in list_:
        if command.startswith(name):
            ret.append(CompletionType(startIndex, name=command, already=len(name)))
    return ret

def get_commandCompletions(startIndex, token):
    from devparrot.core import session
    return _get_callCompletions(session.commands, startIndex, token, CommandCompletion)

def get_macroCompletions(startIndex, tokenName):
    from devparrot.core import session
    return _get_callCompletions(session.macros, startIndex, tokenName, MacroCompletion)

def get_argumentCompletions(callObject, argumentContainer):
    if callObject is None:
        return []

    for i, value in enumerate(argumentContainer.values[:-1]):
        callObject.provide_value(i, value)

    try:
        constraint = callObject.get_constraint(len(argumentContainer.values)-1)
    except IndexError:
        return []
    return constraint.complete_context(argumentContainer.values[-1])


    
def get_completions(text):
    from devparrot.core.command.parserGrammar import parse_input_text
    try:
        pipe = parse_input_text(text)
    except InvalidSyntax:
        return []

    last = pipe.values[-1]
    if last.get_type() == "Identifier":
        return get_commandCompletions(last.index, last.name)

    if last.get_type() == "New":
        return get_commandCompletions(last.index, "")
    
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
                    return get_macroCompletions(lastArg.index, lastArg.name)
                else:
                    return get_argumentCompletions(get_macro(str(lastArg.name)), lastArg)
        except IndexError:
            pass

        return get_argumentCompletions(get_command(str(last.name)), last)
    return []

class ControlerEntryCompletion(CompletionSystem):
    def __init__(self, textWidget):
        CompletionSystem.__init__(self, textWidget)

    def get_completions(self):
        text = self.textWidget.get('1.0', 'insert')
        return get_completions(text)

    def complete(self, completion):
        oldInsert = self.textWidget.index("insert")
        self.textWidget.tk.call(self.textWidget._w, 'insert', "insert", completion.complete())
        self.textWidget.mark_set( 'sel.first', oldInsert)
        self.textWidget.mark_set( 'sel.last', "insert")
        self.textWidget.tag_add( 'sel', oldInsert, "insert")
        
