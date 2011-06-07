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

import gobject
import os,sys

from document import Document
from datetime import datetime
from models.sourceBuffer import SourceBuffer

class TextDocument(Document, gobject.GObject):
	__gproperties__ = {
		'path' : ( gobject.TYPE_STRING,
	                   'Path of the file',
	                   'The absolute path of the file',
	                   None,
		           gobject.PARAM_READWRITE)
	}
	__gsignals__ = {
		'path-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,)),
		'language-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,))
	}
	__models__ = {
		"text" : SourceBuffer
	}
	newFileNumber = 0

	def __init__(self, path=None):
		Document.__init__(self)
		TextDocument.__gobject_init__(self)
		self.path = None
		self.timestamp = None
		self.language = None
		if path:
			self.set_path(path)
		else:
			self.filename = "NewFile%d"%TextDocument.newFileNumber
			TextDocument.newFileNumber += 1

	def __eq__(self, other):
		if self.path and not other.path:
			return False
		if not self.path and other.path:
			return False
		if self.path and other.path :
			return self.path == other.path
		else:
			return self.filename == other.filename
		
	def get_path(self):
		return self.path

	def set_path(self, path):
		import gtksourceview2
		if self.path != path:
			self.path = path
			self.emit('path-changed', self.path)
		languageManager = gtksourceview2.LanguageManager()
		self.language = languageManager.guess_language(self.path, None)
		if self.language:
			self.get_model('text').set_highlight_syntax(True)
			self.get_model('text').set_language(self.language)
			self.emit('language-changed', self.language)

	def has_a_path(self):
		return self.path != None
		
	def get_title(self):
		if self.has_a_path():
			return os.path.basename(self.get_path())
		else:
			return self.filename
		
 	def do_get_property(self, property):
		if property.name == 'path':
			return self.path
		else:
			raise AttributeError, 'unknown property %s' % property.name

	def do_set_property(self, property, value):
		if property.name == 'path':
			self.path = value
			self.filename = os.path.basename(path)
		else:
			raise AttributeError, 'unknown property %s' % property.name

			self.emit('path-changed', self.path)
			
	def get_content(self):
		if not self.path or not os.path.exists(self.path):
			return ""

		text = ""		
		try:
			fileIn = open(self.path, 'r')
			text = fileIn.read()
			fileIn.close()
			self.init_timestamp()
		except:
			sys.stderr.write("Error while loading file %s\n"%self.filename)
		return text

	def init_timestamp(self):
		if self.path:
			self.timestamp = os.stat(self.path).st_mtime
		else:
			self.timestamp = None

	def set_content(self, content):
		if not self.path:
			return
		try :
			fileOut = open(self.path, 'w')
			fileOut.write(content)
			fileOut.close()
			self.init_timestamp()
		except:
			sys.stderr.write("Error while writing file %s\n"%self.path)

	def check_for_exteriorModification(self):
		if not self.path : return None
		if not self.timestamp: return False
		modif = os.stat(self.path).st_mtime
		return  modif > self.timestamp
		
	def load(self):
		self.get_model('text').load_from_document()

	def write(self):
		self.get_model('text').save_to_document()
		
	def check_for_save(self):
		model = self.get_model('text')
		if model.get_modified():
			import mainWindow
			return mainWindow.Helper().ask_questionYesNo("Save document ?", "Document %(documentName)s is changed.\n Do you want to save it?"%{'documentName':self.get_title()})
		return False

	def __str__(self):
		if self.get_path():
			return self.get_path()
		return "None"
		
gobject.type_register(TextDocument)