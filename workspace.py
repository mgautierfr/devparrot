
from textView import TextView

import mainWindow

class Workspace(object):
	def __init__(self):
		self.currentView = TextView()
		mainWindow.workspaceContainer.add(self.currentView.container)

	def set_currentDocument(self, document):
		self.currentView.set_document(document)

	def get_currentDocument(self):
		return self.currentView.get_document()
