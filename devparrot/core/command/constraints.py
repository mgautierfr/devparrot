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

class InvalidToken(Exception):
	def __init__(self, token):
		Exception.__init__(self)
		self.token = token	
	
	def __str__(self):
		return "token %s is invalid"%self.token


class MissingToken(Exception):
	def __init__(self, constraint):
		Exception.__init__(self)
		self.constraint = constraint
	
	def __str__(self):
		return "missing a token for constraint %s"%self.constraint

class TokenParser(object):
	def __init__(self, constraints, askUser=False):
		self.constraints = list(constraints)
		self.status = 0
		self.askUser = askUser
	
	def init(self):
		self.currentConstraint = 0
		for constraint in self.constraints:
			constraint.init()
	
	def get_constraint(self):
		try:
			return self.constraints[self.currentConstraint]
		except IndexError:
			return None
	
	def all_constraints_validated(self):
		for constraint in self.constraints:
			if not constraint.is_consume():
				return False
		return True
	
	def get_tokens_from_constraints(self):
		for constraint in self.constraints:
			yield constraint.token
	
	def advance_constraints(self):
		constraint = self.constraints[self.currentConstraint]
		if constraint.close():
			self.currentConstraint += 1
		else:
			raise MissingToken(constraint)
	
	def close_remaining(self):
		for constraint in self.constraints[self.currentConstraint:]:
			constraint.close(self.askUser)
		
	def check_a_token(self, token):
		constraint = self.get_constraint()
		if constraint is None:
			raise InvalidToken(token)
		if not constraint.check_token(token):
			self.advance_constraints()
			self.check_a_token(token)
	
	def _parse(self, tokens):
		self.init()
		
		for token in tokens:
			print "parse ", token
			self.check_a_token(token)
		
		self.close_remaining()
	
	def check(self, tokens):
		try:
			self._parse(tokens)
		except InvalidToken:
			return False
		except MissingToken:
			return False
		return self.all_constraints_validated()
		

	def parse(self, tokens):
		self._parse(tokens)
		return list(self.get_tokens_from_constraints())
	
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
	def __init__(self, optional=False, multiple=False):
		_Constraint.__init__(self, optional, multiple, None)
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

