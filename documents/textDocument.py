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
from views.textView import TextView
from fileHandle import FileHandle

import glib

class TextDocument(Document, gobject.GObject):
	__gsignals__ = {
		'language-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,)),
		'modified-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'path-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_STRING,)),
	}
	__models__ = {
		"text" : SourceBuffer
	}
	newFileNumber = 0

	def __init__(self, path=None):
		TextDocument.__gobject_init__(self)
		Document.__init__(self)
		self.models['text'].connect('modified-changed', self.on_modified_changed)
		self.fileHandle = None
		self.language = None
		if path:
			self.set_path(path)
			self.load()
		else:
			self.filename = "NewFile%d"%TextDocument.newFileNumber
			TextDocument.newFileNumber += 1
		
		self.add_view('text', TextView(self))

	def __getattr__(self, name):
		if name == "title":
			if self.has_a_path():
				return os.path.basename(self.get_path())
			else:
				return self.filename
		if name == "longTitle":
			if self.has_a_path():
				return self.get_path()
			else:
				return self.filename
		raise AttributeError


	def __eq__(self, other):
		if self.path and not other.path:
			return False
		if not self.path and other.path:
			return False
		if self.path and other.path :
			return self.path == other.path
		else:
			return self.filename == other.filename

	def get_modified(self):
		return self.models['text'].get_modified()

	def add_view(self, model_type, view):
		Document.add_view(self, model_type, view)
		self.currentView.view.connect('focus-in-event', self.on_focus_in_event)

	def on_focus_in_event(self, widget, event):
		res = self.fileHandle.check_for_exteriorModification()
		if res == None : return
		if res:
			import core.mainWindow
			answer = core.mainWindow.Helper().ask_questionYesNo("File content changed",
			     "The content of file %s has changed.\nDo you want to reload it?"%self.title)
			if answer:
				self.load()
			else:
				self.fileHandle.init_timestamp()


	def get_path(self):
		return self.fileHandle.get_path()

	def set_path(self, path):
		import gtksourceview2
		if not self.fileHandle or self.fileHandle.get_path() != path:
			self.fileHandle = FileHandle(path)
			self.emit('path-changed', path)
		languageManager = gtksourceview2.LanguageManager()
		self.language = languageManager.guess_language(path, None)
		if self.language:
			self.models['text'].set_highlight_syntax(True)
			self.models['text'].set_language(self.language)
			self.emit('language-changed', self.language)

	def on_modified_changed(self, buffer):
		self.emit('modified-changed', buffer)

	def has_a_path(self):
		return self.fileHandle.get_path() != None

	def load(self):
		self.models['text'].set_text(self.fileHandle.get_content())

	def write(self):
		model = self.models['text']
		self.fileHandle.set_content(model.get_text(model.get_start_iter(), model.get_end_iter()))
		model.set_modified(False)

	def check_for_save(self):
		model = self.models['text']
		if model.get_modified():
			import mainWindow
			return mainWindow.Helper().ask_questionYesNo("Save document ?", "Document %(documentName)s is changed.\n Do you want to save it?"%{'documentName':self.get_title()})
		return False

	def search(self, backward, text):
		foundIter = self.models['text'].search(backward,text)
		if foundIter:
			self.currentView.view.scroll_to_iter(foundIter, 0.2)

	def goto_line(self, line, delta = None):
		def callback(it):
			self.currentView.view.scroll_to_iter(it, 0.2)
			return False
		if delta != None:
			current_line = self.models['text'].get_iter_at_mark(self.models['text'].get_insert()).get_line()
			if delta == '+':
				line = current_line + line
			if delta == '-':
				line = current_line - line
		line_iter = self.models['text'].get_iter_at_line(line)
		self.models['text'].select_range(line_iter,line_iter)
		glib.idle_add(callback, line_iter)

#	def __str__(self):
#		if self.get_path():
#			return self.get_path()
#		return "None"
		
gobject.type_register(TextDocument)