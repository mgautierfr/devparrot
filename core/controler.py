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
import gtk

import mainWindow

currentSession = None
baseColor = None

#It should be some define of those value somewhere. Where ?
__key_UP__ = 65362
__key_DOWN__ = 65364

def init():
	global baseColor
	mainWindow.entry.connect('activate', on_entry_activate)
	mainWindow.entry.connect('focus-in-event', on_get_focus)
	mainWindow.entry.connect('event', on_entry_event)
	baseColor = mainWindow.entry.get_style().base[gtk.STATE_NORMAL]
	connect_actions()
	pass

def set_session(session):
	global currentSession
	currentSession = session

def connect_actions():
	for action in ActionList:
		for accel in action.accelerators:
			accel.connect_group(mainWindow.accelGroup)

def get_command(commandName):
	for action in ActionList:
		if action.__name__ == commandName:
			return action
	return None
	
def on_get_focus(widget, event, userData = None):
	global baseColor
	widget.modify_base(gtk.STATE_NORMAL,baseColor)
	widget.set_text('')

def on_entry_activate(sourceWidget, userData=None):
	global currentSession
	import gtk
	text = sourceWidget.get_text()
	map = sourceWidget.get_colormap()
	colour = map.alloc_color("red") # light red
	for action in ActionList:
		args = action.regChecker(text)
		if args != None :
			ret = action.run(args)
			if ret == None:
				colour = baseColor
			elif ret:
				colour = map.alloc_color("#BBFFBB") # light green
			else:
				colour = map.alloc_color("#FF9999") # light red
			break
	currentSession.get_history().push(text)
	sourceWidget.modify_base(gtk.STATE_NORMAL,colour)
	if currentSession.get_workspace().get_currentDocument():
		currentSession.get_workspace().get_currentDocument().get_currentView().grab_focus()

def on_entry_event(widget, event, userData = None):
	global currentSession
	import gtk
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
