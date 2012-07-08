#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier


import os
import pyparsing
import grammar

import Tkinter

class noDefault(Exception):
    pass

class _Constraint:
	def __init__(self, optional=False, multiple=False, default=None, askUser=False):
		self.optional = optional
		self.askUser = askUser
		if default is None:
			self.has_default= False
			self.default = self._no_default
		else:
			self.has_default = True
			self.default = default
		self.multiple = multiple
	
	def set_grammar(self, grammar):
		if self.optional or self.askUser or self.has_default:
			if self.multiple:
				self.grammar = pyparsing.Group(pyparsing.ZeroOrMore(grammar))
			else:
				self.grammar = pyparsing.Optional(grammar)
		else:
			if self.multiple:
				self.grammar = pyparsing.Group(pyparsing.OneOrMore(grammar))
			else:
				self.grammar = grammar

	def get_grammar(self):
		return self.grammar

	def _no_default(self):
		raise noDefault()
	
	def _expand_multiple(self, token):
		if self.multiple:
			return [token]
		return token
	
	def check_rawToken(self, token, askUser=False):
		if not token:
			try:
				token = self._expand_multiple(self.default())
				return (True, token)
			except noDefault:
				if askUser and self.askUser:
					token = self.ask_user()
					if token is None:
						print "canceled"
						return (False, token)
					else:
						return (True, token)
			return (self.optional, token)
		if self.multiple:
			ret = True
			tokens = []
			for t in token:
				ret = ret and self.check(t)
				tokens.append(t)
			return (ret, tokens)
		else:
			return (self.check(token), token)

class Default(_Constraint):
	def __init__(self, optional=False):
		_Constraint.__init__(self, optional, False, None)
		self.set_grammar(pyparsing.Word(pyparsing.printables))

	def check(self, rawToken):
		return True
	
	def ask_user(self):
		return None
	
	def complete(self, value):
		if value is None:
			return []
		return [value]

class Keyword(_Constraint):
	def __init__(self, keywords, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(pyparsing.oneOf(" ".join(keywords)))
	
	def check(self, token):
		return True
	
	def ask_user(self):
		return None
			
class File(_Constraint):
	def __init__(self, mode='open', optional=False, multiple=False, default=None):
		def check(s, l, t):
			t = os.path.abspath(t[0])
			if os.path.exists(t):
				return [t]
			d = os.path.dirname(t)
			if mode=='save' and os.path.exists(d):
				return [t]
			raise pyparsing.ParseException(s, l, "wrong file")

		_Constraint.__init__(self, optional, multiple, default, askUser=True)
		self.mode = mode		
		gram = grammar.path.copy()
		gram.setParseAction( check )
		self.set_grammar(gram)
	
	def check(self, token):
		return True

	def ask_user(self):
		from devparrot.core import commandLauncher, ui
		path = None
		currentDoc = commandLauncher.currentSession.get_currentDocument()
		if currentDoc:
			path = currentDoc.get_path()
			if path: path = os.path.dirname(path)
			
		if self.mode=='open':
			token = ui.mainWindow.Helper().ask_filenameOpen(initialdir=path, multiple=self.multiple)
		else:
			token = ui.mainWindow.Helper().ask_filenameSave(initialdir=path)
		return token if token else None
#	
#	def complete(self, value):
#		if value is None:
#			value = ""
#		return [f for f in os.listdir(os.getcwd()) if f.startswith(value)]




class Index(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)		
		self.set_grammar(grammar.fullindex)
		
	
	def check(self, token):
		return True
	
	def ask_user(self):
		return None
	
	def complete(self, value):
		return [value]

class Range(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.indexRange)
	
	def check(self, rawToken):
		return True
	
	def ask_user(self):
		return None
	
	def complete(self, value):
		return [value]

class Integer(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.integer)
		
	
	def check(self, rawToken):
		return True
	
	def ask_user(self):
		return None
	
	def complete(self, value):
		return [value]

class OpenDocument(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.doc)
	
	def check(self, rawToken):
		return True
	
	def ask_user(self):
		return None
	
	def complete(self, value):
		if value is None:
			return []
		return [value]
