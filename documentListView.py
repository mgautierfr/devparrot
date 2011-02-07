
import gtk,pango

class DocumentListView(gtk.TreeView):
	def __init__(self):
		gtk.TreeView.__init__(self)
		cellRenderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn('document', cellRenderer)
		column.set_cell_data_func(cellRenderer, self.cellDataSetter)
		self.append_column(column)
		self.document = None

	def cellDataSetter(self, column, cell, model, iter, user_data=None):
		document = model.get_value(iter, 0)
		cell.props.text = document.get_title()
		if document.get_modified():
			cell.props.weight = pango.WEIGHT_BOLD
		else:
			cell.props.weight = pango.WEIGHT_NORMAL
		pass

	def set_document(self, document):
		self.document = document
		self.set_model(document)
		
