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

from actions import ActionList

import os,sys

import mainWindow
import config

currentSession = None
baseColor = None

def init():
	global baseColor,notFoundColor, okColor, errorColor
	mainWindow.entry.bind('<Return>',on_entry_activate)
	mainWindow.entry.bind('<FocusIn>', on_get_focus)
	mainWindow.entry.bind('<KeyRelease-Up>', on_entry_event)
	mainWindow.entry.bind('<KeyRelease-Down>', on_entry_event)
#	map = mainWindow.entry.get_colormap()
#	baseColor = mainWindow.entry.get_style().base[gtk.STATE_NORMAL]
#	notFoundColor = map.alloc_color(config.get('color','notFoundColor')) # red
#	okColor = map.alloc_color(config.get('color','okColor')) # light green
#	errorColor = map.alloc_color(config.get('color','errorColor')) # light red
	connect_actions()
	pass

def set_session(session):
	global currentSession
	currentSession = session

def connect_actions():
	for action in ActionList:
		for accel in action.accelerators:
			pass
#			accel.connect_group(mainWindow.accelGroup)

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
	found = False
	for action in ActionList:
		args = action.regChecker(text)
		if args != None :
			run_action(text, action.run, args)
			found = True
			break
	if not found:
		pass
		#mainWindow.entry.modify_base(gtk.STATE_NORMAL,notFoundColor)
	currentSession.get_history().push(text)

def get_command(commandName):
	for action in ActionList:
		if action.__name__ == commandName:
			return action
	return None
	
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

def on_entry_event(widget, event, userData = None):
	global currentSession
	#import gtk
	if event.type == gtk.gdk.KEY_PRESS:
		if event.keyval == __key_UP__:
			widget.set_text(currentSession.get_history().get_previous())
			widget.set_position(-1)
			return True
		if event.keyval == __key_DOWN__:
			widget.set_text(currentSession.get_history().get_next())
			widget.set_position(-1)
			return True
	return False
