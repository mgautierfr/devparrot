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

from views.viewContainer import TopContainer,NotebookContainer

import mainWindow

class Workspace(TopContainer):
	def __init__(self):
		TopContainer.__init__(self)

	def set_currentDocument(self, document):
		self.get_currentContainer().set_documentView(document.documentView)

	def get_currentDocument(self):
		child = self.get_currentContainer().get_documentView()
		print child
		if child:
			return child.document
		return None

	def get_currentContainer(self):
		return NotebookContainer.current