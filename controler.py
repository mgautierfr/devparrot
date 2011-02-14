
from textFile import TextFile


from actions import Action

import os

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
		print "running",command.name
		command.run(commands[1:])

