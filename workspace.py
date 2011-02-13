
from views.textView import TextView
from views.viewContainer import ViewContainer

import mainWindow

class Workspace(ViewContainer):
	def __init__(self):
		TextView.current = TextView()
		ViewContainer.__init__(self, TextView.current)
		mainWindow.workspaceContainer.add(self)

	def set_currentDocument(self, document):
		self.get_currentView().set_document(document)

	def get_currentDocument(self):
		return self.get_currentView().get_document()

	def get_currentView(self):
		return TextView.current

	def get_currentViewContainer(self):
		return TextView.current.get_parentContainer()

