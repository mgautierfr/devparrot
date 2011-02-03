
import gtk

class DocumentListView(gtk.TreeView):
	def __init__(self):
		gtk.TreeView.__init__(self)
		cellRenderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn('document', cellRenderer)
		column.add_attribute(cellRenderer, 'text', 0)
		self.append_column(column)
		self.document = None

	def set_document(self, document):
		self.document = document
		self.set_model(document)
		
