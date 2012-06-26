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

class noDefault(Exception):
    pass

class _Contraint:
	def __init__(self, optional=False, multiple=False, default=None, *args, **kwords):
		self.optional = optional
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
	
	def check_rawToken(self, rawToken):
		if rawToken is None and self.default is not None:
			try:
				self.set_token(self.default())
				self.status = 'changed'
				return self.status
			except noDefault:
				pass
		ret =  self.check(rawToken)
		if ret == 'refused' and self.optional:
			self.set_token(rawToken)
			self.status = 'optional'
			return 'optional'
		self.status = ret
		return ret
			
	

class File(_Contraint):
	def __init__(self, mode='open', *args, **kwords):
		_Contraint.__init__(self, *args, **kwords)
		self.mode = mode
	
	def check(self, rawToken):
		if rawToken is None:
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
			return 'changed'
		if os.path.exists(rawToken):
			return self.set_token(os.path.abspath(rawToken))
		else:
			return 'refused'

class Integer(_Contraint):
	def __init__(self, *args, **kwords):
		_Contraint.__init__(self, *args, **kwords)
	
	def check(self, rawToken):
		if rawToken is None:
			return 'refused'
		return self.set_token(int(rawToken))

class OpenDocument(_Contraint):
	def __init__(self, *args, **kwords):
		_Contraint.__init__(self, *args, **kwords)
	
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
