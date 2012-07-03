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

import mainWindow
import config
import utils.event
import re
import shlex

currentSession = None
alias = {}
lineExpenders = []
eventSystem = utils.event.EventSource()


class TkBindLauncher(object):
	def __init__(self, command):
		self.command = command

	def __call__(self, event):
		controler.run_command(self.command)
		return "break"

class EventBindLauncher(object):
	def __init__(self, command):
		self.command = command
	
	def __call__(self, cmdTxt, arg):
		controler.run_command(self.command, cmdTxt=cmdTxt)
		return "break"

TkEventMatcher = re.compile(r"<.*>")

class Binder(object):
	def __init__(self):
		self.tkBinds = {}

	def __setitem__(self, accel, command):
		if TkEventMatcher.match(accel):
			bindLauncher = TkBindLauncher(command)
			if mainWindow.window:
				mainWindow.window.bind_class("Action", accel, bindLauncher)
		else:
			bindLauncher = EventBindLauncher(command)
			eventSystem.connect(accel, bindLauncher)
		self.tkBinds[accel] = bindLauncher

	def bind(self):
		if mainWindow.window:
			for accel, func in self.tkBinds.items():
				if TkEventMatcher.match(accel):
					mainWindow.window.bind_class("Action", accel, func)

	def __delitem__(self, accel):
		if TkEventMatcher.match(accel):
			if mainWindow.window:
				mainWindow.window.unbind_class("Action", accel)
		else:
			eventSystem.event(accel).disconnect(self.binds[accel])
		del self.tkBinds[accel]


binder = Binder()

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

class Controler:
	def __init__(self):
		pass
		
	def tokenize(self, text):
		commandName = None
		for expender in lineExpenders:
			tokens = expender(text)
			if tokens:
				return tokens

		tokenLexer = shlex.shlex(text, posix=True)
		tokenLexer.whitespace_split = True
		commandName = tokenLexer.get_token()
		rawTokens = []
		while True:
			token = tokenLexer.get_token()
			if token is None:
				break
			rawTokens.append(token)

		return (commandName, rawTokens)
		
	def get_command(self, commandName):
		if not commandName:
			return None
		for prio in sorted(alias, reverse=True):
			for aliasName,command in alias[prio]:
				if aliasName == commandName:
					if isinstance(command, basestring):
						token = command
						break
					else:
						return command
		return None
	
	def expand_tokens(self, command, rawTokens):
		print rawTokens
		constraints = command.get_allConstraints()
		rawTokenIter = ListGenerator(rawTokens)
		tokens = []
		ret = 'ok'
		for constraint in constraints:
			print "constraint",constraint
			while True:
				rawToken = rawTokenIter.next()
				print "rawToken",rawToken
				ret = constraint.check_rawToken(rawToken, True)
				print "ret", ret
				if ret != 'again':
					break
				if rawTokenIter.end():
					print "no token break"
					break
			
			if ret in ('end', 'optional'):
				rawTokenIter.back()

			if ret == 'refused':
				print "token refused"
				return False

			tokens.append(constraint.get_token())

		if not rawTokenIter.end():
			print "token left"
			return False
		
		return tokens
	
	def expand_and_complete(self, command, rawTokens):
		constraints = command.get_allConstraints()
		rawTokenIter = ListGenerator(rawTokens)
		completions = []
		for constraint in constraints:
			print "constraint",constraint
			while True:
				rawToken = rawTokenIter.next()
				print "rawToken",rawToken
				ret = constraint.check_rawToken(rawToken, False)
				print "ret", ret
				if ret != 'again':
					break
				if rawTokenIter.end():
					break
			
			if ret in ('ok', 'changed'):
				print "1"
				#good token to good constraint => change constraint
				return [" "]
				continue
			
			if ret == 'refused':
				print "5"
				#bad constraint and madatory => complete and exit
				completions.extend(constraint.complete(rawToken))
				break

			if rawTokenIter.end():
				print "2", ret
				#no more token => complete and change constraint
				completions.extend(constraint.complete(None))
				continue

			if ret == 'optional':
				print "3"
				#bad constraint but optional => complete and change constraint
				completions.extend(constraint.complete(rawToken))
				rawTokenIter.back()
				continue

			if ret == 'end':
				print "4"
				#bad constraint but array => complete and change constraint
				completions.extend(constraint.complete(rawToken))
				rawTokenIter.back()
				continue
			
			
		return completions
			
	
	def launch_command(self, command, cmdText, args):
		eventSystem.event("%s-"%command.__name__)(cmdText, args)
		ret = command.run(cmdText, *args)
		eventSystem.event("%s+"%command.__name__)(cmdText, args)
		return ret
	
	def get_commandCompletions(self, commandName):
		ret = []
		for prio in sorted(alias, reverse=True):
			for aliasName,command in alias[prio]:
				if aliasName.startswith(commandName):
					ret.append(aliasName)
		return ret
	
	def run_command(self, text, cmdText=None):
		commandName, rawTokens = self.tokenize(text)
		command  = self.get_command(commandName)
		if command is None:
			return None
		if cmdText is not None:
			commandName = cmdText
		if not command.pre_check(commandName):
			return False
		tokens = self.expand_tokens(command, rawTokens)
		if tokens == False:
			print "refused"
			return False
		ret = None

		ret = self.launch_command(command, commandName, tokens)
		currentSession.get_history().push(text)
		return ret
		
	def get_completions(self, text):
		commandName, rawTokens = self.tokenize(text)
		command = self.get_command(commandName)
		if command is None:
			return self.get_commandCompletions(commandName if commandName else "")
		return self.expand_and_complete(command, rawTokens)
		
		
controler = Controler()

def init():
	pass

def set_session(session):
	global currentSession
	currentSession = session
	eventSystem.event('newSession')(session)
	
def run_command(text):
	return controler.run_command(text)

def get_completions(text):
	return controler.get_completions(text)
