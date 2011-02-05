

from documentManager import DocumentManager
from workspace import Workspace

import controler

class Session(object):
	def __init__(self):
		self.documentManager = DocumentManager(self)
		self.workspace = Workspace()
		controler.set_session(self)

	def get_workspace(self):
		return self.workspace

	def get_documentManager(self):
		return self.documentManager

	def get_currentDocument(self):
		return self.workspace.get_currentDocument()
