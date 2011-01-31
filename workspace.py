
from textView import TextView

class Workspace(object):
	def __init__(self, workspaceContainer):
		self.container = workspaceContainer
		self.currentView = TextView()
		self.container.add(self.currentView.container)

	def set_currentDocument(self, textFile):
		self.currentView.set_document(textFile)

	def get_currentDocument(self):
		return self.currentView.get_document()
