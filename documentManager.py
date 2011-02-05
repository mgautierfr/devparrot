
import gtk,gobject
from textFile import TextFile

class DocumentManager(gtk.ListStore):
	def __init__(self, session):
		gtk.ListStore.__init__(self,gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
		self.session = session

	def get_file(self, path, autoOpen = True):
		for title,document in self:
			if document.path == path:
				return document
		if autoOpen :
			f = TextFile(path)
			self.prepend([f.get_title(),f])
			return f
		return None

	def del_file(self, document):
		it = self.get_iter_first()
		while(self.get_value(it,1).get_path() != document.get_path()):
			it.get_next()
		del self[it]
			

	def new_file(self):
		f = TextFile()
		self.prepend([f.get_title(),f])
		return f
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for (title,doc) in self])
		}
