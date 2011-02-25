
import gtk,gobject
from textFile import TextFile

import mainWindow, controler

class DocumentManager(gtk.ListStore):
	def __init__(self, session):
		gtk.ListStore.__init__(self, gobject.TYPE_PYOBJECT)
		self.session = session
		mainWindow.documentListView.set_document(self)
		self.signalConnections = {}

	def force_redraw(self, doc):
		path = doc.get_rowReference().get_path()
		self.row_changed(path, self.get_iter(path))

	def on_path_changed(self, source, path):
		self.force_redraw(source)

	def on_event(self, source):
		self.force_redraw(source.get_document())

	def get_file(self, path, autoOpen = True):
		for (document,) in self:
			if document.path == path:
				return (document, False)
		if autoOpen :
			doc = TextFile(path)
			self.signalConnections[doc] = {
				'path-changed' : ( doc, doc.connect('path-changed', self.on_path_changed) ),
				'modified-changed' : ( doc.get_model('text'), doc.get_model('text').connect('modified-changed', self.on_event) )
			}
			self.append([doc])
			doc.set_rowReference(gtk.TreeRowReference(self,len(self)-1))
			return (doc, True)
		return (None,None)

	def del_file(self, document):
		rowReference = document.get_rowReference()
		if document.check_for_save():
			controler.interprete('save')
		for (key, (obj,connect)) in self.signalConnections[document].items():
			obj.disconnect(connect)
		del self.signalConnections[document]
		self.remove(self.get_iter(rowReference.get_path()))
			

	def new_file(self):
		doc = TextFile()
		self.signalConnections[doc] = {
			'path-changed' : ( doc, doc.connect('path-changed', self.on_path_changed) ),
			'modified-changed' : ( doc.get_model('text'), doc.get_model('text').connect('modified-changed', self.on_event) )
		}
		self.append([doc])
		doc.set_rowReference(gtk.TreeRowReference(self,len(self)-1))
		return doc
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (doc) in self])
		}
