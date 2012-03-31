
import re

class Index:
	def __init__(self, textWidget, indice, indexCallNeeded = False):
		self.textWidget = textWidget
		if not indexCallNeeded:
			try:
				split = indice.split('.')
				self._split = (int(split[0]), int(split[1]))
				self._indice = indice
			except ValueError:
				indexCallNeeded = True

		if indexCallNeeded:
			self._indice = textWidget.index(indice)
			split = self._indice.split('.')
			self._split = (int(split[0]), int(split[1]))
	
	def __str__(self):
		return self._indice
	
	def __repr__(self):
		return "<Index instance pos "+self._indice+">"
	
	def __lt__(self, other):
		if other is None : return False
		try:
			return self._split < other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split < _other._split

	def __le__(self, other):
		if other is None : return False
		try:
			return self._split <= other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split <= _other._split

	def __eq__(self, other):
		if other is None : return False
		try:
			return self._split == other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split == _other._split

	def __ne__(self, other):
		if other is None : return False
		try:
			return self._split != other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split != _other._split

	def __gt__(self, other):
		if other is None : return False
		try:
			return self._split > other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split > _other._split
			
	def __ge__(self, other):
		if other is None : return False
		try:
			return self._split >= other._split
		except AttributeError:
			_other = Index(self.textWidget, other)
			return self._split >= _other._split
	
	def __add__(self, other):
		return Index(self.textWidget, "%s + %s"%(self._indice, other), True)
		
	def __sub__(self, other):
		return Index(self.textWidget, "%s - %s"%(self._indice, other), True)
	
		
class Mark:
	def __init__(self, textWidget):
		self.textWidget = textWidget

class Tag:
	def __init__(self, textWidget):
		self.textWidget = textWidget




