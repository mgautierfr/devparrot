#!/usr/bin/python

import gtk, gobject
import os,sys

class TextFile(gtk.TextBuffer):
	newFileNumber = 0
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
		'file-saved'   : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())
	}

	def __init__(self, path = None):
		gtk.TextBuffer.__gobject_init__(self)
		if path:
			self.path = path
			self.filename = os.path.basename(path)
		else:
			self.path = None
			self.filename = "NewFile%d"%TextFile.newFileNumber
			TextFile.newFileNumber += 1

	def get_title(self):
		return self.filename

	def get_path(self):
		return self.path

	def set_path(self, path):
		if self.path != path:
			self.path = path
			self.filename = os.path.basename(path)
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

	def load(self):
		if self.path and os.path.exists(self.path):
			try:
				fileIn = open(self.path, 'r')
				text = fileIn.read()
				fileIn.close()

				self.set_text(text)
				self.set_modified(False)
			except:
				sys.stderr.write("Error while loading file %s\n"%self.filename)
		else:
			self.set_text("")

	def write(self):
		if not self.path : return
		self.writeTo(self.path)
		self.set_modified(False)

	def writeTo(self, path):
		text = self.get_text(self.get_start_iter(), self.get_end_iter())
		try :
			fileOut = open(path, 'w')
			fileOut.write(text)
			fileOut.close()
			self.emit('file-saved')
		except:
			sys.stderr.write("Error while writing file %s\n"%path)

	def __str__(self):
		if self.get_path():
			return self.get_path()
		return "None"

gobject.type_register(TextFile)
