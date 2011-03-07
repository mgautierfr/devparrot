#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier


from views.textView import TextView
from views.viewContainer import ViewContainer,LeafContainer

import mainWindow

class Workspace(ViewContainer):
	def __init__(self):
		LeafContainer.current = LeafContainer(TextView())
		ViewContainer.__init__(self, LeafContainer.current)
		mainWindow.workspaceContainer.add(self)

	def set_currentDocument(self, document):
		self.get_currentView().set_document(document)

	def get_currentDocument(self):
		return self.get_currentView().get_document()

	def get_currentView(self):
		return LeafContainer.current.get_view()

	def get_currentViewContainer(self):
		return LeafContainer.current.get_parentContainer()

