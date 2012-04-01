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

import os,sys

class FileDocSource(object):
	def __init__(self, path):
		self.path = os.path.abspath(path)
		self.timestamp = None
		
	def __getattr__(self, name):
		if name == "title":
			return os.path.basename(self.path)
		if name == "longTitle":
			return self.path
		raise AttributeError
		
	def __eq__(self, other):
		if self.__class__ == other.__class__:
			return self.path == other.path
		return False
		
	def get_path(self):
		return self.path

	def has_path(self):
		return True
	
	def get_content(self):
		if not os.path.exists(self.path):
			return ""

		text = ""
		try:
			fileIn = open(self.path, 'r')
			text = fileIn.read()[:-1]
			fileIn.close()
			self.init_timestamp()
		except:
			sys.stderr.write("Error while loading file %s\n"%self.filename)
		return text
	

	def init_timestamp(self):
		self.timestamp = os.stat(self.path).st_mtime

	def set_content(self, content):
		try :
			fileOut = open(self.path, 'w')
			fileOut.write(content.encode('utf8'))
			fileOut.close()
			self.init_timestamp()
			return True
		except:
			sys.stderr.write("Error while writing file %s\n"%self.path)
			return False
	
	def need_reload(self):
		if not self.timestamp: return False
		modif = os.stat(self.path).st_mtime
		return  modif > self.timestamp


