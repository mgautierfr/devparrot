#    This file is part of CodeCollab.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    CodeCollab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CodeCollab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CodeCollab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

from textFile import TextFile

from actions import Action

import os,sys

import mainWindow

currentSession = None

def init():
	mainWindow.entry.connect('activate', on_entry_activate)
	connect_actions()
	pass

def set_session(session):
	global currentSession
	currentSession = session

def connect_actions():
	for (name, action) in Action.actionList.items():
		if action.accelerator :
			mainWindow.accelGroup.connect_group(action.accelerator[0], action.accelerator[1],
			                                    accel_flags=0,
			                                    callback=action.callback)

def on_entry_activate(sourceWidget, userData=None):
	interprete(sourceWidget.get_text())
	sourceWidget.set_text('')
	currentSession.get_workspace().get_currentView().grab_focus()

def get_command(commandStr=''):
	if commandStr in Action.actionList :
		return Action.actionList[commandStr]
	return None
		
def interprete(cmdline):
	commands = cmdline.split(' ')
	command = get_command(commands[0])
	if command :
		command.run(commands[1:])
	else:
		sys.stderr.write("can't found command named %s\n"%commands[0])

