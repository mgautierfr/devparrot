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

class FileHandle(object):
	def __init__(self, path):
		self.path = path
		self.timestamp = None
		
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
