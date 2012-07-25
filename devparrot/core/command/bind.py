import capi
import re

TkEventMatcher = re.compile(r"<.*>")

class TkBindLauncher(object):
	def __init__(self, command):
		self.command = command

	def __call__(self, event):
		from devparrot.core import commandLauncher
		commandLauncher.run_command(self.command)
		return "break"

class EventBindLauncher(object):
	def __init__(self, command):
		self.command = command
	
	def __call__(self, arg):
		from devparrot.core import commandLauncher
		commandLauncher.run_command(self.command)
		return "break"

class Binder(object):
	def __init__(self):
		self.tkBinds = {}

	def __setitem__(self, accel, command):		
		if TkEventMatcher.match(accel):
			from devparrot.core import ui
			bindLauncher = TkBindLauncher(command)
			if ui.mainWindow.window:
				ui.mainWindow.window.bind_class("Command", accel, bindLauncher)
		else:
			from devparrot.core import commandLauncher
			bindLauncher = EventBindLauncher(command)
			commandLauncher.eventSystem.connect(accel, bindLauncher)
		self.tkBinds[accel] = bindLauncher

	def bind(self):
		from devparrot.core import ui
		if ui.mainWindow.window:
			for accel, func in self.tkBinds.items():
				if TkEventMatcher.match(accel):
					ui.mainWindow.window.bind_class("Command", accel, func)

	def __delitem__(self, accel):
		if TkEventMatcher.match(accel):
			from devparrot.core import ui
			if ui.mainWindow.window:
				ui.mainWindow.window.unbind_class("Command", accel)
		else:
			from devparrot.core import commandLauncher
			commandLauncher.eventSystem.event(accel).disconnect(self.binds[accel])
		del self.tkBinds[accel]



