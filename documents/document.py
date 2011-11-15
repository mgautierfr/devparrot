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

from datetime import datetime
import ttk
import core.mainWindow

class Document(object):
	def __init__(self, documentSource):
		self.models = {}
		self.titleVar = ttk.Tkinter.StringVar()
		self.titleVar.set(documentSource.longTitle)
		self.modifiedVar = ttk.Tkinter.StringVar(value="normal")
		self.documentView = DocumentView(self)
		self.models['text'] = ttk.Tkinter.Text(core.mainWindow.workspaceContainer)
		self.models['text'].bind("<<Modified>>", self.on_modified_changed)
		self.views = []
		self.currentView = None
		
		self.set_path(documentSource)
		self.load()

		self.add_view('text', TextView(self))
	
	def __getattr__(self, name):
		if name in ["title", "longTitle"]:
			return self.documentSource.__getattr__(name)
		raise AttributeError
	
	def __eq__(self, other):
		if other == None : return False
		return self.documentSource == other.documentSource
		
	def add_view(self, model_type, view):
		if self.currentView != None:
			print "NYI : Only one view per document for now"
			return
		self.views.append(view)
		view.set_model(self.models[model_type])
		self.documentView.set_view(view)
		self.currentView = view
		#view.view.connect_after('focus-in-event', self.on_focus_in_event)
		
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
			self.titleVar.set(self.documentSource.longTitle)
		if False:
			self.models['text'].set_language(self.documentSource.language)
			self.models['text'].set_highlight_syntax(True)
		#except AttributeError:
		#	self.models['text'].set_highlight_syntax(False)
		
	def load(self):
		self.models['text'].delete("0.1", "end")
		self.models['text'].insert("0.1", self.documentSource.get_content())
		self.models['text'].edit_modified(False)
	
	def write(self):
		model = self.models['text']
		if self.documentSource.set_content(model.get_text(model.get_start_iter(), model.get_end_iter())):
			model.set_modified(False)
			return True
		return False
		
	def on_modified_changed(self, event):
		self.documentView.set_bold(self.models['text'].edit_modified())
	
	def on_focus_in_event(self, widget, event):
		res = self.documentSource.need_reload()
		if res:
			import core.mainWindow
			answer = core.mainWindow.Helper().ask_questionYesNo("File content changed",
			     "The content of file %s has changed.\nDo you want to reload it?"%self.title)
			if answer:
				ctx = self.currentView.get_context()
				self.load()
				#glib.idle_add(self.currentView.set_context, ctx)

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
			return True
		return False

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