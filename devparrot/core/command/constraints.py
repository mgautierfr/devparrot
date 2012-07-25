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
	
	def init(self):
		if self.multiple:
			self.token = []
		else:
			self.token = None
		self.consume = False
	
	def set_token(self, token):
		if self.consume:
			raise InvalidToken(token)
		if self.multiple:
			self.token.append(token)
		else:
			self.token = token
			self.consume = True
	
	def set_grammar(self, grammar):
		self.grammar = grammar.setResultsName("result") + pyparsing.StringEnd()
	
	def close(self, askUser=False):
		if self.is_consume():
			return True
		if self.multiple and len(self.token):
			self.consume = True
			return True
		try:
			self.set_token(self.default())
			return self.close()
		except noDefault:
			if askUser and self.askUser:
				token = self.ask_user()
				if token is not None:
					self.token = token
					self.consume = True
					return self.close()
		if self.optional:
			self.consume = True
			return self.close()
		raise MissingToken(self)
	
	def is_consume(self):
		return self.consume

	def _no_default(self):
		raise noDefault()
	
	def check_token(self, token):
		if self.is_consume():
			return False
		if not token:
			if self.optional:
				self.set_token(None)
				return True
			return False

		if self.token and not self.multiple:
			return False
		
		try:
			parsed = self.grammar.parseString(token)
		except pyparsing.ParseException:
			return False
		self.set_token(parsed.get("result"))
		return True
	
	def check(self, token):
		return True
	
	def ask_user(self):
		return None

class Default(_Constraint):
	def __init__(self, optional=False, multiple=False, default=None):
		_Constraint.__init__(self, optional, multiple, default)
		self.set_grammar(pyparsing.Word(pyparsing.printables))


class Keyword(_Constraint):
	def __init__(self, keywords, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.keywords = keywords
		self.set_grammar(pyparsing.oneOf(" ".join(keywords)))
	
	def __str__(self):
		return "Keyword <%s>"%self.keywords
	
	def __repr__(self):
		return "<Constraint.Keyword %s>"%self.keywords

class Boolean(_Constraint):
	def __init__(self, true=["True", "true", "1"], false=["False", "false", "0"], *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.true = true
		self.false = false
		
		def check(s, l, t):
			if t[0] in self.true:
				return [True]
			if t[0] in self.false:
				return [False]
			raise  pyparsing.ParseException(s, l, "invalid value")
		
		gram = pyparsing.oneOf(" ".join(self.true+self.false))
		gram.setParseAction(check)
		self.set_grammar(gram)
			
class File(_Constraint):
	OPEN, SAVE, NEW = xrange(3)
	def __init__(self, mode=OPEN, optional=False, multiple=False, default=None):
		try:
			(x for x in mode)
		except TypeError:
			mode = (mode,)
		def check(s, l, t):
			t = os.path.abspath(t[0])
			if os.path.exists(t):
				return [t]
			d = os.path.dirname(t)
			if File.SAVE in mode and os.path.exists(d):
				return [t]
			if File.NEW in mode:
				return [t]
			raise pyparsing.ParseException(s, l, "wrong file")

		_Constraint.__init__(self, optional, multiple, default, askUser=True)
		self.mode = mode		
		gram = grammar.path.copy()
		gram.setParseAction( check )
		self.set_grammar(gram)

	def ask_user(self):
		from devparrot.core import commandLauncher, ui
		path = None
		currentDoc = commandLauncher.currentSession.get_currentDocument()
		if currentDoc:
			path = currentDoc.get_path()
			if path: path = os.path.dirname(path)
			
		if File.SAVE in self.mode:
			token = ui.mainWindow.Helper().ask_filenameSave(initialdir=path)
		else:
			token = ui.mainWindow.Helper().ask_filenameOpen(initialdir=path, multiple=self.multiple)
		return token if token else None


class Index(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.fullindex)

class Range(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.indexRange)
	
class Integer(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.integer)

class OpenDocument(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.set_grammar(grammar.doc)

