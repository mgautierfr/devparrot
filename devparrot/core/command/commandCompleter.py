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

from devparrot.core.completion import Completion, CompletionSystem


class CommandCompletion(Completion):
    def __init__(self, *args, **kwords):
        Completion.__init__(self,*args, **kwords)

    def __str__(self):
        return "%s "%self.value

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

def get_tokenCompletions(tokenName):
    from devparrot.core import session
    ret = []
    for command in session.commands:
        if command.startswith(tokenName):
            ret.append(CommandCompletion(value=command, final=True))
    return ret

def get_commandCompletions(functionCall):
    command = get_command(str(functionCall.name))
    if command is None:
        return (0, [])

    try:
        constraint = command.get_constraint(len(functionCall.values)-1)
    except IndexError:
        return (0, [])
    return constraint.complete_context(functionCall.values[-1])
    
def get_completions(text):
    from devparrot.core.command.parserGrammar import parse_input_text
    pipe = parse_input_text(text)
    if pipe is None:
        return (None, [])

    if pipe.get_type() == "New":
        return (pipe.index, get_tokenCompletions(""))

    last = pipe.values[-1]
    if last.get_type() == "Identifier":
        return (last.index, get_tokenCompletions(last.name))
    
    if last.get_type() == 'CommandCall':
        return get_commandCompletions(last)
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
        
