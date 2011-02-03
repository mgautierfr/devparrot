
import gtk,gobject
from file import TextFile

class DocumentManager(gtk.ListStore):
	def __init__(self, session):
		gtk.ListStore.__init__(self,gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
		self.session = session

	def get_file(self, path):
		for title,document in self:
			if document.path == path:
				return document
		f = TextFile(path)
		self.prepend([f.get_title(),f])
		return f
			

	def new_file(self):
		f = TextFile()
		self.prepend([f.get_title(),f])
		return f
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (title,doc) in self])
		}
