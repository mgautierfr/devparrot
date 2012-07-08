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

class Session(object):
	class History(object):
		def __init__(self):
			self.history = list()
			self.currentIndex = 0

		def push(self, line):
			self.history.append(line)
			self.currentIndex = 0

		def get_previous(self):
			if self.currentIndex < len(self.history):
				self.currentIndex += 1
			if self.currentIndex==0 : return ""
			return self.history[-self.currentIndex]

		def get_next(self):
			if self.currentIndex != 0:
				self.currentIndex -= 1
			if self.currentIndex == 0 : return ""
			return self.history[-self.currentIndex]

	def __init__(self):
		import documentManager
		import ui.workspace
		import commandLauncher
		self.documentManager = documentManager.DocumentManager(self)
		self.workspace = ui.workspace.Workspace()
		self.history = Session.History()
		commandLauncher.set_session(self)

	def get_workspace(self):
		return self.workspace

	def get_documentManager(self):
		return self.documentManager

	def get_currentDocument(self):
		return self.workspace.get_currentDocument()
		
	def get_history(self):
		return self.history

