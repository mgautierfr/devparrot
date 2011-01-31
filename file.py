#!/usr/bin/python

import gtk
import os,sys

from document import Document

class TextFile(Document):
	newFileNumber = 0
	def __init__(self, path = None):
		if path:
			self.set_path(path)
		else:
			self.path = None
			self.filename = "NewFile%d"%TextFile.newFileNumber
			TextFile.newFileNumber += 1
		self.buffer = gtk.TextBuffer()
		self.load()

	def get_model(self):
		return self.buffer

	def get_title(self):
		return self.filename

	def is_modified(self):
		return self.buffer.get_modified()

	def get_path(self):
		return self.path

	def set_path(self, path):
		self.path = path
		self.filename = os.path.basename(path)

	def load(self):
		if self.path and os.path.exists(self.path):
			try:
				fileIn = open(self.path, 'r')
				text = fileIn.read()
				fileIn.close()

				self.buffer.set_text(text)
				self.buffer.set_modified(False)
			except:
				sys.stderr.write("Error while loading file %s\n"%self.filename)
		else:
			self.buffer.set_text("")

	def write_to(self, path):
		text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter())
		
		try :
			fileOut = open(path, 'w')
			fileOut.write(text)
			fileOut.close()
			self.buffer.set_modified(False)
			self.set_path(path)
		except:
			sys.stderr.write("Error while writing file %s\n"%path)

	def __str__(self):
		if self.get_path():
			return self.get_path()
		return "None"
