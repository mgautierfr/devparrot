
import gtk,pango

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
		self.connect("button-press-event", self.discard, None)

	def discard(self, widget, event, user_data=None):
		return True

	def cellDocumentSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.get_title()
		if document.get_modified():
			cell.props.weight = pango.WEIGHT_BOLD
		else:
			cell.props.weight = pango.WEIGHT_NORMAL

	def cellPathSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.get_rowReference().get_path()[0]
		cell.set_fixed_size(10,-1)

	def set_document(self, document):
		self.document = document
		self.set_model(document)
		
