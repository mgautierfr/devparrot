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

import gtk,gobject
from textFile import TextFile

import mainWindow

class DocumentManager(gtk.ListStore):
	def __init__(self, session):
		gtk.ListStore.__init__(self, gobject.TYPE_PYOBJECT)
		self.session = session
		mainWindow.documentListView.set_document(self)
		self.signalConnections = {}

	def find_index(self, doc):
		index = 0
		for row in self:
			if row[0] == doc:
				return index
			index += 1
		return None

	def force_redraw(self, doc):
		path = self.find_index(doc)
		if path:
			self.row_changed(path, self.get_iter(path))

	def on_path_changed(self, source, path):
		self.force_redraw(source)

	def on_event(self, source):
		self.force_redraw(source.get_document())

	def has_file(self, path):
		for (document,) in self:
			if document.path == path:
				return True
		return False

	def get_file(self, path):
		for (document,) in self:
			if document.path == path:
				return document
		return None

	def del_file(self, document):
		rowReference = self.find_index(document)
		for (key, (obj,connect)) in self.signalConnections[document].items():
			obj.disconnect(connect)
		del self.signalConnections[document]
		del self[rowReference]
			

	def new_file(self, path=None):
		doc = TextFile(path)
		self.signalConnections[doc] = {
			'path-changed' : ( doc, doc.connect('path-changed', self.on_path_changed) ),
			'modified-changed' : ( doc.get_model('text'), doc.get_model('text').connect('modified-changed', self.on_event) )
		}
		self.append([doc])
		return doc
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (doc) in self])
		}
