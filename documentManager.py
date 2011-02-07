
import gtk,gobject
from textFile import TextFile

import mainWindow

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
		self.force_redraw(source)

	def get_file(self, path, autoOpen = True):
		print "looking for path", path
		for (document,) in self:
			print "checking doc", document.path
			if document.path == path:
				return (document, False)
		if autoOpen :
			doc = TextFile(path)
			self.signalConnections[doc] = {
				'path-changed' : doc.connect('path-changed', self.on_path_changed),
				'changed' : doc.connect('changed', self.on_event),
				'file-saved' : doc.connect('file-saved', self.on_event)
			}
			self.append([doc])
			doc.set_rowReference(gtk.TreeRowReference(self,len(self)-1))
			return (doc, True)
		return (None,None)

	def del_file(self, document):
		rowReference = document.get_rowReference()
		for (key, connect) in self.signalConnections[document].items():
			document.disconnect(connect)
		del self.signalConnections[document]
		self.remove(self.get_iter(rowReference.get_path()))
			

	def new_file(self):
		doc = TextFile()
		self.signalConnections[doc] = {
			'path-changed' : doc.connect('path-changed', self.on_path_changed),
			'changed' : doc.connect('changed', self.on_event),
			'file-saved' : doc.connect('file-saved', self.on_event)
		}
		self.append([doc])
		print len(self)
		doc.set_rowReference(gtk.TreeRowReference(self,len(self)-1))
		return doc
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (doc) in self])
		}
