
from Tkinter import TclError
from collections import namedtuple
from error import BadArgument

_Index = namedtuple('Index', "line col")

class Index(_Index):
	def __new__(self, textWidget, index, indexCallNeeded = False):
		"""
		Construct an index.
		@param textWidget the textWidget associated to the index. Used only to the construction of index. Not stored
		@param index the index text we want to store
		@param indexCallNeeded directly use textWidget.insert instead of try to split the text
		"""
		if not indexCallNeeded:
			try:
				_split = index.split('.')
				split = (int(_split[0]), int(_split[1]))
			except ValueError:
				indexCallNeeded = True
			except IndexError:
				raise BadArgument()

		if indexCallNeeded:
			try:
				index = textWidget.index(index)
				_split = index.split('.')
				split = (int(_split[0]), int(_split[1]))
			except TclError:
				raise BadArgument()
		return _Index.__new__(self, *split)

	def __str__(self):
		return "%d.%d"%self
	
	def __repr__(self):
		return "<Index instance pos %s>"%str(self)

#	def __add__(self, other):
#		return Index(self.textWidget, "%s + %s"%(self._index, other), True)
#
#	def __sub__(self, other):
#		return Index(self.textWidget, "%s - %s"%(self._index, other), True)
