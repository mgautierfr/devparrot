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

from views.documentView import DocumentView
from views.textView import TextView
from models.sourceBuffer import SourceBuffer

import gobject
from datetime import datetime

class Document(gobject.GObject):
	__gsignals__ = {
		'modified-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'documentSource-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		                    (gobject.TYPE_PYOBJECT,)),
	}
	
	def __init__(self, documentSource):
		Document.__gobject_init__(self)
		self.models = {}
		self.models['text'] = SourceBuffer(self)
		self.models['text'].connect('modified-changed', self.on_modified_changed)
		self.documentView = DocumentView(self)
		self.views = []
		self.currentView = None
		
		self.set_path(documentSource)
		self.load()

		self.add_view('text', TextView(self))
		self.emit
	
	def __getattr__(self, name):
		if name in ["title", "longTitle"]:
			return self.documentSource.__getattr__(name)
		raise AttributeError
	
	def __eq__(self, other):
		return self.documentSource == other.documentSource
		
	def add_view(self, model_type, view):
		if self.currentView != None:
			print "NYI : Only one view per document for now"
			return
		self.views.append(view)
		view.set_model(self.models[model_type])
		self.documentView.set_view(view)
		self.currentView = view
		view.view.connect('focus-in-event', self.on_focus_in_event)
		
	def remove_view(self, model_type, view):
		if self.models[model_type] in self.views.keys():
			self.views[self.models[model_type]].remove(view)
		self.documentView.remove_view(view)
		view.set_model(None)
		if self.currentView == view : self.currentView = None
		
	def get_currentView(self):
		return self.currentView
		
	def get_modified(self):
		return self.models['text'].get_modified()
	
	def has_a_path(self):
		return self.documentSource.get_path() != None
	
	def get_path(self):
		return self.documentSource.get_path()
	
	def set_path(self, documentSource):
		if (not "documentSource" in self.__dict__ or
		    self.documentSource != documentSource):
			self.documentSource = documentSource
			self.emit('documentSource-changed', self.documentSource)
		try:
			self.models['text'].set_language(self.documentSource.language)
			self.models['text'].set_highlight_syntax(True)
		except AttributeError:
			self.models['text'].set_highlight_syntax(False)
		
	def load(self):
		self.models['text'].set_text(self.documentSource.get_content())
	
	def write(self):
		model = self.models['text']
		self.documentSource.set_content(model.get_text(model.get_start_iter(), model.get_end_iter()))
		model.set_modified(False)
		
	def on_modified_changed(self, buffer):
		self.emit('modified-changed', buffer)
	
	def on_focus_in_event(self, widget, event):
		res = self.documentSource.need_reload()
		if res:
			import core.mainWindow
			answer = core.mainWindow.Helper().ask_questionYesNo("File content changed",
			     "The content of file %s has changed.\nDo you want to reload it?"%self.title)
			if answer:
				self.load()

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

gobject.type_register(Document)