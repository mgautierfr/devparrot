

class View(object):
	def __init__(self):
		self.document = None
	
	def get_document(self):
		return self.document

	def set_document(self, document):
		self.document = document
		self.set_model(document.get_model())
