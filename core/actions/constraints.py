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
import core.controler
import core.mainWindow

import Tkinter

class noDefault(Exception):
    pass

class _Constraint:
	def __init__(self, optional=False, multiple=False, default=None, *args, **kwords):
		self.optional = optional
		if default is None:
			self.default = self._no_default
		else:
			self.default = default
		self.multiple = multiple
		self.init()
	
	def init(self):
		if self.multiple:
			self.token = []
		else:
			self.token = None
	
	def get_token(self):
		return self.token
	
	def set_token(self, value):
		if self.multiple:
			self.token.append(value)
			return 'again'
		self.token = value
		return 'ok'

	def _no_default(self):
		raise noDefault()
	
	def check_rawToken(self, rawToken, askUser):
		if rawToken is None:
			self.status = 'refused'
			if self.multiple and len(self.token):
				self.status = 'end'
			else:
				try:
					self.set_token(self.default())
					self.status = 'changed'
				except noDefault:
					if askUser:
						self.status = self.ask_user()
				if self.status == 'refused' and self.optional:
					self.status = 'optional'
			return self.status

		self.status = self.check(rawToken)

		if self.status == 'refused':
			print self.multiple, self.token
			if self.multiple and len(self.token):
				self.status = 'end'
			elif self.optional:
				self.status = 'optional'
				try:
					self.set_token(self.default())
					self.status = 'changed'
				except noDefault:
					pass
		return self.status

class Default(_Constraint):
	def __init__(self, optional=False):
		_Constraint.__init__(self, optional, False, None)
	
	def check(self, rawToken):
		if rawToken is None:
			return 'refused'
		return self.set_token(rawToken)
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		if value is None:
			return []
		return [value]
			
	

class File(_Constraint):
	def __init__(self, mode='open', *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		self.mode = mode
	
	def check(self, rawToken):
		if os.path.exists(rawToken):
			return self.set_token(os.path.abspath(rawToken))
		else:
			return 'refused'
	
	def ask_user(self):
		path = None
		currentDoc = core.controler.currentSession.get_currentDocument()
		if currentDoc:
			path = currentDoc.get_path()
			if path: path = os.path.dirname(path)
			
		if self.mode=='open':
			self.token = core.mainWindow.Helper().ask_filenameOpen(initialdir=path, multiple=self.multiple)
		else:
			self.token = core.mainWindow.Helper().ask_filenameSave(initialdir=path)
		if not self.token:
			return 'refused'
		return 'ok'
	
	def complete(self, value):
		if value is None:
			value = ""
		return [f for f in os.listdir(os.getcwd()) if f.startswith(value)]

class Index(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
	
	def check(self, rawToken):
		import utils.annotations
		currentDoc = core.controler.currentSession.get_currentDocument()
		if not currentDoc:
			return 'refused'
		try:
			index = utils.annotations.Index(currentDoc.get_model(), rawToken)
		except utils.annotations.BadArgument:
			return 'refused'
		return self.set_token(index)
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		return [value]

class Range(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		import re
		self.regexp = re.compile(r"(.*):(.*)")
	
	def check(self, rawToken):
		import utils.annotations
		currentDoc = core.controler.currentSession.get_currentDocument()
		if not currentDoc:
			return 'refused'
		match = self.regexp.match(rawToken)
		if not match:
			return 'refused'
		
		start, end = match.groups()
		try:
			startIndex = utils.annotations.Index(currentDoc.get_model(), start)
			endIndex = utils.annotations.Index(currentDoc.get_model(), end)
			_range =  utils.annotations.Range(currentDoc.get_model(), startIndex, endIndex)
		except utils.annotations.BadArgument:
			return 'refused'
		return self.set_token(_range)
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		return [value]

class RangeText(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
		import re
		self.regexp = re.compile(r"\[(.*)\]")
	
	def check(self, rawToken):
		import utils.annotations
		currentDoc = core.controler.currentSession.get_currentDocument()
		if not currentDoc:
			return 'refused'
		match = self.regexp.match(rawToken)
		if not match:
			print "noMatch"
			return 'refused'
		rangeText = match.group(1)
		rangeConstraint = Range()
		rangeConstraint.init()
		if rangeConstraint.check(rangeText) == 'refused':
			print "norange", rangeText
			return 'refused'
		range_ = rangeConstraint.get_token()
		token = range_.textWidget.get(range_.startIndex, range_.endIndex)
		return self.set_token(token)
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		return [value]

class Integer(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
	
	def check(self, rawToken):
		if rawToken is None:
			return 'refused'
		return self.set_token(int(rawToken))
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		return [value]

class OpenDocument(_Constraint):
	def __init__(self, *args, **kwords):
		_Constraint.__init__(self, *args, **kwords)
	
	def check(self, rawToken):
		try:
			index =  int(rawToken)
			document = core.controler.currentSession.get_documentManager().get_nthFile(index)
			if document is None:
				return 'refused'
		except ValueError:
			if not os.path.exists(rawToken):
				return 'refused'
			path = os.path.abspath(rawToken)
			if not core.controler.currentSession.get_documentManager().has_file(path):
				return 'refused'
			document = core.controler.currentSession.get_documentManager().get_file(path)

		return self.set_token(document)
	
	def ask_user(self):
		return 'refused'
	
	def complete(self, value):
		if value is None:
			return []
		return [value]
