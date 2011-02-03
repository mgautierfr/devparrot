
from textFile import TextFile

import actions.controllerActions
import actions.actionDef
import os

class Controler(object):
	def __init__(self, session, mainWindow):
		self.session = session
		self.entry = mainWindow.entry
		self.helper = mainWindow.helper
		self.accelGroup = mainWindow.accelGroup
		self.entry.connect('activate', self.on_entry_activate)
		self.connect_actions()

	def connect_actions(self):
		for (name, action) in actions.actionDef.Action.actionList.items():
			if action.accelerator :
				self.accelGroup.connect_group(action.accelerator[0], action.accelerator[1],
				                              accel_flags=0,
				                              callback=action.get_callback(self.session, self.helper))

	def on_entry_activate(self, sourceWidget, userData=None):
		self.interprete(sourceWidget.get_text())
		sourceWidget.set_text('')

	def get_command(self, commandStr=''):
		if commandStr in actions.actionDef.Action.actionList :
			return actions.actionDef.Action.actionList[commandStr]
		return None
		
	def interprete(self, cmdline):
		commands = cmdline.split(' ')
		command = self.get_command(commands[0])
		if command :
			print "running",command.name
			command.run(self.session, self.helper, commands[1:])

