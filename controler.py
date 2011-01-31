
from file import TextFile
import os

class Controler(object):
	def __init__(self, session, mainWindow):
		self.session = session
		self.entry = mainWindow.entry
		self.helper = mainWindow.helper
		self.entry.connect('activate', self.on_entry_activate)

	def on_entry_activate(self, sourceWidget, userData=None):
		self.interprete(sourceWidget.get_text())
		sourceWidget.set_text('')

	def get_commands_list(self):
		return [ com for com in dir(self) if com[:4] == "com_"]

	def get_command(self, commandStr=''):
		l = [com for com in self.get_commands_list() if com[4:].startswith(commandStr)]
		if len(l) == 1:
			return l[0]
		return None
		

	def interprete(self, cmdline):
		commands = cmdline.split(' ')
		command = self.get_command(commands[0])
		if command :
			print "running",command
			exec 'self.%(command)s(%(args)s)'%{'command':command,'args':'commands[1:]'}

	def com_save(self, args=[]):
		if not self.session.get_currentDocument():
			return
		if len(args)>=1:
			fileToSave = os.path.abspath(args[0])
		else:
			fileToSave = self.session.get_currentDocument().get_path()
			if not fileToSave:
				fileToSave = self.helper.ask_filenameSave("Save")

		self.session.get_currentDocument().write_to(fileToSave)
				
	def com_new(self, args=[]):
		f = self.session.get_documentManager().new_file()
		self.session.get_workspace().set_currentDocument(f)
	
	def com_debug(self, args=[]):
		print self.session.get_documentManager()
	
	def com_quit(self, args=[]):
		import gtk
		gtk.main_quit()

	def com_open(self, args=[]):
		fileToOpen = None
		if len(args)>=1:
			fileToOpen = os.path.abspath(args[0])
		if not fileToOpen:
			fileToOpen = self.helper.ask_filenameOpen("Open a file")
		if not fileToOpen : return

		f = self.session.get_documentManager().get_file(fileToOpen)
		self.session.get_workspace().set_currentDocument(f)
