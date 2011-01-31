

from documentManager import DocumentManager
from workspace import Workspace

class Session(object):
	def __init__(self, workspaceContainer):
		self.documentManager = DocumentManager(self)
		self.workspace = Workspace(workspaceContainer)

	def get_workspace(self):
		return self.workspace

	def get_documentManager(self):
		return self.documentManager

	def get_currentDocument(self):
		return self.workspace.get_currentDocument()
