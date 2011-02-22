

class Document():
	def __init__(self):
		self.models = {}
		pass
		
	def get_model(self,repr_type):
		if repr_type not in self.__class__.__models__:
			raise KeyError()
		if repr_type not in self.models:
			self.models[repr_type] = self.__class__.__models__[repr_type](self)
		return self.models[repr_type] 