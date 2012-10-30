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

from command.splitter import Splitter, Token
from completion import Completion

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
        
    def tokenize(self, text, faultTolerent=False):
        splitted = list(Splitter(text, faultTolerent))
        if splitted:
            commandName = splitted[0]

        return (commandName, splitted[1:])
        
    def get_command(self, commandName):
        extraArgs = []
        if not commandName:
            return None
        for prio in sorted(alias, reverse=True):
            for aliasName, command in alias[prio]:
                if aliasName == commandName:
                    if isinstance(command, basestring):
                        args = command.split(' ')
                        commandName = args[0]
                        for arg in args[1:]:
                            token = Token(startIndex=len(commandName)+1, value=arg)
                            extraArgs.append(token)
                        break
                    else:
                        return (command, extraArgs)
        return None
    
    def expand_tokens(self, command, rawTokens):
        import command.grammar as grammarModule
        rangeExpander = grammarModule.rangeExpander
        for token in rawTokens:
            token.value = rangeExpander.transformString(token.value)
        tokenParser = command.get_tokenParser()
        tokens = tokenParser.parse(rawTokens)
        return tokens

    def expand_and_complete(self, command, rawTokens):
        tokenParser = command.get_tokenParser()
        completions = tokenParser.complete(rawTokens)
        return completions
    
    def launch_command(self, command, args):
        eventSystem.event("%s-"%command.__name__)(args)
        ret = command.run(*args)
        eventSystem.event("%s+"%command.__name__)(args)
        return ret
    
    def get_commandCompletions(self, commandName):
        ret = []
        for prio in sorted(alias, reverse=True):
            for aliasName, command in alias[prio]:
                if aliasName.startswith(commandName):
                    token = Completion(value=aliasName, final=True)
                    ret.append(token)
        return (0, ret)
    
    def run_command(self, text):
        from command.tokenParser import MissingToken
        print text
        commandName, rawTokens = self.tokenize(text)
        try:
            command, extraArgs  = self.get_command(commandName.value)
        except AttributeError:
            return None
        except TypeError:
            return None
        rawTokens = extraArgs + rawTokens
        if not command.pre_check():
            return False
        try:
            tokens = self.expand_tokens(command, rawTokens)
        except MissingToken, e:
            print "Input missing for argument %s" % e.constraint
            return False
        if tokens == False:
            print "refused"
            return False
        ret = None

        ret = self.launch_command(command, tokens)
        self.history.push(text)
        return ret
        
    def get_completions(self, text):
        commandName, rawTokens = self.tokenize(text, True)
        if not rawTokens:
            return self.get_commandCompletions(commandName.value if commandName else "")
        command = self.get_command(commandName.value)
        if command is None:
            return (0, [])
        (command, extraArgs) = command
        rawTokens = extraArgs + rawTokens
        if not command.pre_check():
            return (0, [])
        return self.expand_and_complete(command, rawTokens)



