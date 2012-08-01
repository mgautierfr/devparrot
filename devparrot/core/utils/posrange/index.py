
from Tkinter import TclError
from collections import namedtuple
from error import BadArgument

Index_ = namedtuple('Index', "line col text")

class _Index(Index_):
	__slots__ = ()

	def __str__(self):
		return self.text
	
	def __repr__(self):
		return "<Index instance pos %s>"%str(self)

	def __eq__(self, other):
		return self.text == other.text

	def __ne__(self, other):
		return not( self.text == other.text )

def Index(textWidget, index, indexCallNeeded = False):
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
	return _Index(split[0], split[1], index)

