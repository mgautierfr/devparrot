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

currentSession = None
baseColor = None
alias = {}

class Binder(object):
	def __init__(self):
		pass

	def __setitem__(self, accel, command):
		def run_and_break(event):
			run_command(command)
			return "break"
		mainWindow.window.bind_class("Action", accel, run_and_break)

binder = Binder()

def add_alias(regex, command, prio=2):
	import re
	cregex = re.compile(r"%s"%regex)
	if prio not in alias:
		alias[prio] = []
	alias[prio].append((cregex, command)) 

def init():
	global baseColor,notFoundColor, okColor, errorColor
	import core.actions
	mainWindow.entry.bind('<Return>',on_entry_activate)
	mainWindow.entry.bind('<FocusIn>', on_get_focus)
	mainWindow.entry.bind('<KeyRelease-Up>', on_entry_event)
	mainWindow.entry.bind('<KeyRelease-Down>', on_entry_event)
#	map = mainWindow.entry.get_colormap()
#	baseColor = mainWindow.entry.get_style().base[gtk.STATE_NORMAL]
#	notFoundColor = map.alloc_color(config.get('color','notFoundColor')) # red
#	okColor = map.alloc_color(config.get('color','okColor')) # light green
#	errorColor = map.alloc_color(config.get('color','errorColor')) # light red
	pass

def set_session(session):
	global currentSession
	currentSession = session

def run_action(text, function,*args, **keywords):
	ret = function(*args,**keywords)
#	if ret == None:
#		mainWindow.entry.modify_base(gtk.STATE_NORMAL,baseColor)
#	elif ret:
#		mainWindow.entry.modify_base(gtk.STATE_NORMAL,okColor)
#	else:
#		mainWindow.entry.modify_base(gtk.STATE_NORMAL,errorColor)
	mainWindow.entry.delete(0,'end')
	mainWindow.entry.insert('end',text)
	
def run_command(text):
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
		mainWindow.window.event_generate("<<%s->>"%command.__name__)
		command.run(cmdText, *args)
		mainWindow.window.event_generate("<<%s+>>"%command.__name__)
		
	tokens = text.split()
	command = get_command(tokens[0])
	if command:
		launch_command(command, tokens[0], [expand_token(t) for t in tokens[1:]])
	currentSession.get_history().push(text)
	
def on_get_focus(event):
	global baseColor
	#event.widget.modify_base(gtk.STATE_NORMAL,baseColor)
	event.widget.delete(0,'end')

def on_entry_activate(event):
	global currentSession
	text = event.widget.get()
	run_command(text)	
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
