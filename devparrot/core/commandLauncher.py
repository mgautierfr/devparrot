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

import utils.event

from completion import Completion, CommandCompletion

alias = {}
eventSystem = utils.event.EventSource()

def add_alias(aliasName, command, prio=2):
    if prio not in alias:
        alias[prio] = []
    alias[prio].append((aliasName, command)) 


class ListGenerator:
    def __init__(self, l):
        self.l = l
        self.index = 0
        self.bend = (len(l) == 0)
    
    def next(self):
        if self.index >= len(self.l):
            self.bend = True
            return None
        self.index += 1
        return self.l[self.index-1]
    
    def back(self):
        self.index = max(0, self.index-1)
    
    def end(self):
        return self.index >= len(self.l)

class History(object):
    def __init__(self):
        self.history = list()
        self.currentIndex = 0

    def push(self, line):
        self.history.append(line)
        self.currentIndex = 0

    def get_previous(self):
        if self.currentIndex < len(self.history):
            self.currentIndex += 1
        if self.currentIndex == 0:
            return ""
        return self.history[-self.currentIndex]

    def get_next(self):
        if self.currentIndex != 0:
            self.currentIndex -= 1
        if self.currentIndex == 0:
            return ""
        return self.history[-self.currentIndex]

class CommandLauncher:
    def __init__(self):
        self.history = History()
        
    def get_command(self, commandName):
        from devparrot.core import session
        if not commandName:
            return None
        return session.commands.get(commandName, None)

    def get_tokenCompletions(self, tokenName):
        from devparrot.core import session
        ret = []
        for command in session.commands:
            if command.startswith(tokenName):
                ret.append(CommandCompletion(value=command, final=True))
        return ret

    def get_commandCompletions(self, functionCall):
        command = self.get_command(str(functionCall.name))
        if command is None:
            return (0, [])

        try:
            constraint = command.get_constraint(len(functionCall.values)-1)
        except IndexError:
            return (0, [])
        return constraint.complete_context(functionCall.values[-1])
        
    def get_completions(self, text):
        from devparrot.core.command.parserGrammar import parse_input_text
        context = parse_input_text(text)
        if context is None:
            return (None, [])

        if context.get_type() == "Identifier":
            return (context.index, self.get_tokenCompletions(context.name))
        if context.get_type() == "New":
            return (context.index, self.get_tokenCompletions(""))
        if context.get_type() == 'CommandCall':
            context = context.get_last_commandCall()
            if context:
                return self.get_commandCompletions(context)
        return (None, [])

    def run_command(self, text):
        from devparrot.core import session
        from devparrot.core.command.parserGrammar import rewrite_command
        rewrited = rewrite_command(text)
        if rewrited is not None:
            exec(rewrited,dict(session.commands), {})
            self.history.push(text)

