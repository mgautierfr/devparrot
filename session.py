#    This file is part of CodeCollab.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    CodeCollab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CodeCollab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CodeCollab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

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
