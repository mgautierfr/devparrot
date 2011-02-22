
import gtk,pango

import controler

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


	def switch_to_document(self, widget, event, user_data=None):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			selection = widget.get_selection()
			select = selection.get_selected()
			if select:
				(model, iter) = select
				document = model.get_value(iter, 0)
				controler.currentSession.get_workspace().set_currentDocument(document)

	def cellDocumentSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.get_title()

	def cellPathSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.get_rowReference().get_path()[0]
		cell.set_fixed_size(10,-1)

	def set_document(self, document):
		self.document = document
		self.set_model(document)
		
