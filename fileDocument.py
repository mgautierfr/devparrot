#    This file is part of CodeCollab.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    CodeCollab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CodeCollab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CodeCollab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

import gobject
import os,sys

from document import Document
from datetime import datetime

class FileDocument(Document, gobject.GObject):
	__gproperties__ = {
		'path' : ( gobject.TYPE_STRING,
	                   'Path of the file',
	                   'The absolute path of the file',
	                   None,
		           gobject.PARAM_READWRITE)
	}
	__gsignals__ = {
		'path-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,))
	}
	def __init__(self):
		Document.__init__(self)
		FileDocument.__gobject_init__(self)
		self.path = None
		self.timestamp = None
		
	def get_path(self):
		return self.path

	def set_path(self, path):
		if self.path != path:
			self.path = path
			self.emit('path-changed', self.path)
		
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

	def __str__(self):
		if self.get_path():
			return self.get_path()
		return "None"
		
gobject.type_register(FileDocument)