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


import mainWindow

class DocumentManager(object):
	def __init__(self, session):
		self.session = session
		self.view = mainWindow.documentListView
		self.documents = []
		self.signalConnections = {}
	
	def get_nbDocuments(self):
		return len(self.documents)
	
	def get_nthFile(self, index):
		return self.documents[index]

	def find_index(self, doc):
		index = 0
		for document in self.documents:
			if document == doc:
				return index
			index += 1
		return None

	def has_file(self, path):
		for document in self.documents:
			if document.get_path() == path:
				return True
		return False

	def get_file(self, path):
		for document in self.documents:
			if document.get_path() == path:
				return document
		return None

	def del_file(self, document):
		try:
			self.documents.remove(doc)
			return True
		except:
			return False
	
	def switch_to_document(self, index):
		document = self.documents[index]
		if document.documentView.is_displayed():
			document.documentView.focus()
		else:
			core.controler.currentSession.get_workspace().set_currentDocument(document)
			

	def add_file(self, document):
		self.documents.append(document)
		self.view.insert('', 'end', text=str(self.documents.index(document)), values=(document.title))
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (doc) in self])
		}
