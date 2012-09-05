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

import os,sys

import utils.event

from command.splitter import Splitter, Token
from command.constraints import Completion

currentSession = None
alias = {}
lineExpenders = []
eventSystem = utils.event.EventSource()

def add_alias(aliasName, command, prio=2):
	if prio not in alias:
		alias[prio] = []
	alias[prio].append((aliasName, command)) 

def add_expender(expender):
	lineExpenders.append(expender)


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
		return self.bend


def getcommonstart(seq):
    if not seq:return ""
    s1, s2 = min(seq), max(seq)
    l = min(len(s1), len(s2))
    if l == 0 :
        return ""
    for i in xrange(l) :
        if s1[i] != s2[i] :
            return s1[:i]
    return s1[:l]


class Controler:
	def __init__(self):
		pass
		
	def tokenize(self, text, faultTolerent=False):
		commandName = None
		for expender in lineExpenders:
			tokens = expender(text)
			if tokens:
				return tokens

		splitted = list(Splitter(text, faultTolerent))
		if splitted:
			commandName = splitted[0]

		return (commandName, splitted[1:])
		
	def get_command(self, commandName):
		extraArgs = []
		if not commandName:
			return None
		for prio in sorted(alias, reverse=True):
			for aliasName,command in alias[prio]:
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
		import command.grammar as grammarModule
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
			for aliasName,command in alias[prio]:
				if aliasName.startswith(commandName):
					token = Completion(value=aliasName, final=True)
					ret.append(token)
		return (0, ret)
	
	def run_command(self, text):
		from command.tokenParser import MissingToken
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
			print "Input missing for argument %s"%e.constraint
			return False
		if tokens == False:
			print "refused"
			return False
		ret = None

		ret = self.launch_command(command, tokens)
		currentSession.get_history().push(text)
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
		
		
controler = Controler()

def init():
	pass

def set_session(session):
	global currentSession
	currentSession = session
	eventSystem.event('newSession')(session)
	
def run_command(text):
	if isinstance(text, basestring):
		commands = text.split('\n')
	else:
		commands = []
		map(commands.extend, [s.split('\n') for s in text])
	ret = None
	for cmd in commands[:-1]:
		ret = controler.run_command(cmd)
		if not ret:
			return ret
	import ui.mainWindow
	ui.mainWindow.entry.textVariable.set(commands[-1])
	if commands[-1]:
		ui.mainWindow.entry.focus()
		ui.mainWindow.entry.icursor("end")
	return ret

def get_completions(text):
	start, completions = controler.get_completions(text)
	return (start, getcommonstart([str(c) for c in completions]), completions)
