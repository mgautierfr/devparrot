#!/usr/bin/python

import gtk, gobject
import os,sys

from fileDocument import FileDocument
from models.sourceBuffer import SourceBuffer

class TextFile(FileDocument):
	__gsignals__ = {
		'language-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,))
	}
	__models__ = {
		"text" : SourceBuffer
	}
	newFileNumber = 0

	def __init__(self, path = None):
		FileDocument.__init__(self)
		self.rowReference = None
		self.path = None
		self.language = None
		if path:
			self.set_path(path)
		else:
			self.filename = "NewFile%d"%TextFile.newFileNumber
			TextFile.newFileNumber += 1

	def get_rowReference(self):
		return self.rowReference
	
	def __eq__(self, other):
		if self.path and not other.path:
			return False
		if not self.path and other.path:
			return False
		if self.path and other.path :
			return self.path == other.path
		else:
			return self.filename == other.filename

	def set_rowReference(self, rowReference):
		self.rowReference = rowReference

	def get_title(self):
		if self.get_path():
			return os.path.basename(self.get_path())
		else:
			return self.filename

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

	def set_path(self, path):
		import gtksourceview2
		FileDocument.set_path(self, path)
		languageManager = gtksourceview2.LanguageManager()
		self.language = languageManager.guess_language(self.path, None)
		if self.language:
			self.get_model('text').set_highlight_syntax(True)
			self.get_model('text').set_language(self.language)
