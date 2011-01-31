
from document import Document
from file import TextFile

class DocumentManager(Document):
	def __init__(self, session):
		self.session = session
		self.documents = {}

	def get_file(self, path):
		if path in self.documents:
			return self.documents[path]
		f = TextFile(path)
		self.documents[path] = f
		return f
			

	def new_file(self):
		f = TextFile()
		self.documents[f.get_title()] = f
		return f
	
	def __str__(self):
		return "Open Files\n[\n%(openfiles)s\n]"%{
			'openfiles' : "\n".join([str(doc) for doc in self.documents])
		}
