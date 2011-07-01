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

import gtk,pango

import core.controler

class DocumentListView(gtk.TreeView):
	def __init__(self):
		gtk.TreeView.__init__(self)
		cellDocumentRenderer = gtk.CellRendererText()
		cellDocumentRenderer.props.xalign = 0
		cellPathRenderer = gtk.CellRendererText()
		(width, height) = cellPathRenderer.get_fixed_size()
		cellPathRenderer.set_fixed_size(10,-1)
		column = gtk.TreeViewColumn('document')
		column.pack_start(cellPathRenderer)
		column.pack_start(cellDocumentRenderer)
		column.set_cell_data_func(cellDocumentRenderer, self.cellDocumentSetter)
		column.set_cell_data_func(cellPathRenderer, self.cellPathSetter)
		self.append_column(column)
		self.props.headers_visible = False
		self.props.can_focus = False
		cellDocumentRenderer.props.sensitive = True
		self.document = None
		self.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.connect("button-press-event", self.switch_to_document, None)
		self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('documentView',gtk.TARGET_SAME_APP,5)], gtk.gdk.ACTION_COPY)
		self.connect('drag-begin',self.on_drag_begin)
		self.connect('drag-data-get',self.on_drag_data_get)
		self.connect('drag-end',self.on_drag_end)
		


	def switch_to_document(self, widget, event, user_data=None):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			selection = widget.get_selection()
			select = selection.get_selected()
			if select:
				(model, iter) = select
				document = model.get_value(iter, 0)
				if document.documentView.is_displayed():
					document.documentView.grab_focus()
				else:
					core.controler.currentSession.get_workspace().set_currentDocument(document)
	
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


	def cellDocumentSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.title
		cell.props.weight = pango.WEIGHT_BOLD if document.get_modified() else pango.WEIGHT_NORMAL

	def cellPathSetter(self, column, cell, model, iter, user_data=None):
		path = model.get_path(iter)
		cell.props.text = path[0]
		cell.set_fixed_size(10,-1)

	def set_document(self, document):
		self.document = document
		self.set_model(document)
		
