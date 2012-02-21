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

import Tkinter,ttk

import core.controler

documentListView = None

def activate():
	core.controler.eventSystem.connect('newSession', on_new_session)

def on_new_session(session):
	global documentListView
	documentManager = core.controler.currentSession.get_documentManager()
	documentListView = DocumentListView(core.mainWindow.window)
	documentManager.connect('documentDeleted', documentListView.on_documentDeleted)
	documentManager.connect('documentAdded', documentListView.on_documentAdded)
	core.mainWindow.add_helper(documentListView, 'left')
	pass

def deactivate():
	pass


class DocumentListView(ttk.Treeview):
	class PseudoList(object):
		def __init__(self, ttkTreeView):
			self.view = ttkTreeView

		def __len__(self):
			return len(self.view.get_children(''))

		def __getitem__(self, key):
			return self.view.get_children('')[key]

		def __delitem__(self, key):
			self.view.detach(self.__getitem__(key))

		def sort(self):
			sorted_ = sorted(self)
			for i in range(len(self)):
				del self[0]
			for i,p in enumerate(sorted_):
				self.view.reattach(p, '', i)
				self.view.item(p, text="%d"%i)


	def __init__(self,parent):
		ttk.Treeview.__init__(self,parent)
		self['columns'] = ('name')
		self.column('#0', width=30, stretch=False)
		self.heading('#0', text="id")
		self.heading('name', text="document")
		self['selectmode'] =(Tkinter.BROWSE)
		self.bind('<Double-Button-1>', self.on_double_click)
		#self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('documentView',gtk.TARGET_SAME_APP,5)], gtk.gdk.ACTION_COPY)
		#self.connect('drag-begin',self.on_drag_begin)
		#self.connect('drag-data-get',self.on_drag_data_get)
		#self.connect('drag-end',self.on_drag_end)

	def on_documentAdded(self, document):
		ttk.Treeview.insert(self, '', 'end', iid=document.get_path(), text="0", values=(document.title))
		self.sort()

	def on_documentDeleted(self,document):
		self.delete(document.get_path())
		self.sort()

	def on_double_click(self, event):
		selection = self.selection()
		if selection:
			document = core.controler.currentSession.get_documentManager().get_file(selection[0])
			core.controler.currentSession.get_documentManager().switch_to_document(document)
	
	def on_drag_begin(self, widget, drag_context, data=None):
		import core.controler
		selection = widget.get_selection()
		select = selection.get_selected()
		if select:
			(model, iter) = select
			document = model.get_value(iter, 0)
			core.controler.currentSession.get_workspace().prepare_to_dnd(True,document.documentView)

	def on_drag_data_get(self, widget, drag_context, selection_data, info, time, data=None):
		selection = widget.get_selection()
		select = selection.get_selected()
		if select:
			(model, iter) = select
			document = model.get_value(iter, 0)
			selection_data.set('documentView', info, document.longTitle)
		else:
			return False
	
	def on_drag_end(self, widget, drag_context, data=None):
		import core.controler
		core.controler.currentSession.get_workspace().prepare_to_dnd(False)

	def sort(self):
		DocumentListView.PseudoList(self).sort()

