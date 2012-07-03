
import re
import Tkinter

class BadArgument(Exception):
    pass

class Index:
	def __init__(self, textWidget, index, indexCallNeeded = False):
		self.textWidget = textWidget
		if not indexCallNeeded:
			try:
				split = index.split('.')
				self._split = (int(split[0]), int(split[1]))
				self._index = index
			except ValueError:
				indexCallNeeded = True
			except IndexError:
				raise BadArgument()

		if indexCallNeeded:
			try:
				self._index = textWidget.index(index)
				split = self._index.split('.')
				self._split = (int(split[0]), int(split[1]))
			except Tkinter.TclError:
				raise BadArgument()
	
	def __str__(self):
		return self._index
	
	def __repr__(self):
		return "<Index instance pos "+self._index+">"
	
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
		return Index(self.textWidget, "%s + %s"%(self._index, other), True)
		
	def __sub__(self, other):
		return Index(self.textWidget, "%s - %s"%(self._index, other), True)

class Range:
	def __init__(self, textWidget, startIndex, endIndex):
		self.textWidget = textWidget
		self.startIndex = startIndex
		self.endIndex = endIndex
	
	def __str__(self):
		return "%s:%s"%(self.startIndex, self.endIndex)
	
	def __repr__(self):
		return "<Range instance pos "+self._index+">"
	
		
class Mark:
	def __init__(self, textWidget, name='insert'):
		self.textWidget = textWidget
		self.name = name

class Tag:
	def __init__(self, textWidget, name, start='insert', stop='insert'):
		self.textWidget = textWidget
		self.name = name
		self.start = start
		self.stop = stop
