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

from ui.documentView import DocumentView
from devparrot.views.textView import TextView
import commandLauncher

from datetime import datetime
import ttk
import utils.event
import utils.variable
from devparrot.models.sourceBuffer import SourceBuffer


class Document(utils.event.EventSource):
	def __init__(self, documentSource):
		utils.event.EventSource.__init__(self)
		self.models = {}
		self.title = utils.variable.ProxyVar(self.get_title)
		self.longTitle = utils.variable.ProxyVar(self.get_longTitle)
		self.set_path(documentSource)
		self.modifiedVar = utils.variable.Variable("normal")
		self.documentView = DocumentView(self)
		self.models['text'] = SourceBuffer(self)
		self.models['text'].bind("<<Modified>>", self.on_modified_changed)
		self.views = []
		self.currentView = None	
		self.add_view('text', TextView(self))
		commandLauncher.eventSystem.event("newDocument")(self)
	
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
		view.view.bind("<FocusIn>", self.on_focus_in_event, add="+")
		
	def remove_view(self, model_type, view):
		if self.models[model_type] in self.views.keys():
			self.views[self.models[model_type]].remove(view)
		self.documentView.remove_view(view)
		view.set_model(None)
		if self.currentView == view : self.currentView = None
		
	def get_currentView(self):
		return self.currentView

	def get_model(self):
		return self.models['text']
	
	def get_title(self):
		return self.documentSource.title
	
	def get_longTitle(self):
		return self.documentSource.longTitle
	
	def has_a_path(self):
		return self.documentSource.has_path()
	
	def get_path(self):
		return self.documentSource.get_path()
	
	def set_path(self, documentSource):
		if (not "documentSource" in self.__dict__ or
		    self.documentSource != documentSource):
			try:
				oldPath = self.documentSource.get_path()
			except AttributeError:
				oldPath = None
			self.documentSource = documentSource
			self.title.notify()
			self.longTitle.notify()
			self.event('textSet')(self)
			self.event('pathChanged')(self, oldPath)
		
	def load(self):
		self.models['text'].set_text(self.documentSource.get_content())
		self.currentView.set_lineNumbers()
	
	def write(self):
		model = self.models['text']
		if self.documentSource.set_content(model.get_text()):
			model.edit_modified(False)
			return True
		return False
		
	def on_modified_changed(self, event):
		self.documentView.set_bold(self.models['text'].edit_modified())
	
	def on_focus_in_event(self, event):
		res = self.documentSource.need_reload()
		if res:
			import ui.mainWindow
			answer = ui.mainWindow.Helper().ask_questionYesNo("File content changed",
			     "The content of file %s has changed.\nDo you want to reload it?"%self.title)
			if answer:
				#ctx = self.currentView.get_context()
				self.load()
				#glib.idle_add(self.currentView.set_context, ctx)

	def check_for_save(self):
		model = self.models['text']
		if model.edit_modified():
			import ui.mainWindow
			return ui.mainWindow.Helper().ask_questionYesNo("Save document ?", "Document %(documentName)s is changed.\n Do you want to save it?"%{'documentName':self.get_title()})
		return False
		
	def search(self, backward, text):
		if self.models['text'].search(backward,text):
			self.currentView.view.see("insert")
			return True
		return False

	def goto_index(self, index):
		self.currentView.view.mark_set("insert", index)
		self.currentView.view.see(index)


