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

currentSession = None
alias = {}
lineExpenders = []
eventSystem = utils.event.EventSource()

class BindLauncher(object):
	def __init__(self, command):
		self.command = command

	def __call__(self, event):
		run_command(self.command)
		return "break"

class Binder(object):
	def __init__(self):
		self.binds = {}

	def __setitem__(self, accel, command):
		self.binds[accel] = BindLauncher(command)
		if mainWindow.window:
			mainWindow.window.bind_class("Action", accel, self.binds[accel])

	def bind(self):
		if mainWindow.window:
			for accel, func in self.binds.items():
				mainWindow.window.bind_class("Action", accel, func)

	def __delitem__(self, accel):
		if mainWindow.window:
			mainWindow.window.unbind_class("Action", accel)
		del self.binds[accel]


binder = Binder()

def add_alias(regex, command, prio=2):
	import re
	cregex = re.compile(r"%s"%regex)
	if prio not in alias:
		alias[prio] = []
	alias[prio].append((cregex, command)) 

def add_expender(expender):
	lineExpenders.append(expender)

def init():
	import core.actions
	mainWindow.entry.bind('<Return>',on_entry_activate)
	mainWindow.entry.bind('<FocusIn>', on_get_focus)
	mainWindow.entry.bind('<KeyRelease-Up>', on_entry_event)
	mainWindow.entry.bind('<KeyRelease-Down>', on_entry_event)
	pass

def set_session(session):
	global currentSession
	currentSession = session
	eventSystem.event('newSession')(session)
	
def run_command(text):
	def find_tokens():
		for expender in lineExpenders:
			tokens = expender(text)
			if tokens:
				return tokens
		return text.split()
	def get_command(token):
		for prio in sorted(alias, reverse=True):
			for reg,command in alias[prio]:
				if reg.match(token):
					if isinstance(command, basestring):
						token = command
						break
					else:
						return command
		return None
	def expand_token(token):
		return token
	def launch_command(command, cmdText, args):
		eventSystem.event("%s-"%command.__name__)(cmdText, args)
		ret = command.run(cmdText, *args)
		eventSystem.event("%s+"%command.__name__)(cmdText, args)
		return ret
	
	tokens = find_tokens()
	command = get_command(tokens[0])
	ret = None
	if command:
		ret = launch_command(command, tokens[0], [expand_token(t) for t in tokens[1:]])
	currentSession.get_history().push(text)
	return ret
	
def on_get_focus(event):
	global baseColor
	event.widget['style'] = ""
	event.widget.delete(0,'end')

def on_entry_activate(event):
	global currentSession
	text = event.widget.get()
	ret = run_command(text)
	if ret is None:
		event.widget['style'] = "notFoundStyle.TEntry"
	elif ret:
		event.widget['style'] = "okStyle.TEntry"
	else:
		event.widget['style'] = "errorStyle.TEntry"
	if currentSession.get_workspace().get_currentDocument():
		currentSession.get_workspace().get_currentDocument().get_currentView().focus()

def on_entry_event(event):
	global currentSession
	event.widget.delete("0", "end")
	if event.keysym == "Up":
		event.widget.insert("end", currentSession.get_history().get_previous())
		return True
	if event.keysym == "Down":
		event.widget.insert("end", currentSession.get_history().get_next())
		return True
	return False



