
from file import TextFile

class DocumentManager(object):
	def __init__(self, session):
		self.session = session
		self.documents = []

	def get_file(self, path):
		for document in self.documents:
			if document.path == path:
				return document
		f = TextFile(path)
		self.documents.insert(0,f)
		return f
			

	def new_file(self):
		f = TextFile()
		self.documents.insert(0,f)
		return f
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for doc in self.documents])
		}
