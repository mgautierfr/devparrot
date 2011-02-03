
import gtk,pango

class TextView(object):
	def __init__(self):
		self.document = None 

		self.container = gtk.VBox()
		self.label = gtk.Label()
		self.label.set_selectable(True)
		self.label.set_alignment(0, 0.5)
		self.scrolledwindow = gtk.ScrolledWindow()
		self.textview = gtk.TextView()
		self.scrolledwindow.add(self.textview)
		self.container.add(self.label)
		self.container.add(self.scrolledwindow)

		self.container.child_set_property(self.label, "expand", False)
		self.container.show_all()
		self.signalConnections = {}

	def get_document(self):
		return self.document

	def on_path_changed(self, path, userData=None):
		if self.document.get_path():
			self.label.set_text(self.document.get_path())
		else:
			self.label.set_text(self.document.get_title())

	def set_bold(self, sourceGadget, bold):
		att = pango.AttrList()
		att.insert(pango.AttrWeight(pango.WEIGHT_BOLD if bold else pango.WEIGHT_NORMAL,
		                            start_index=0,
		                            end_index=len(self.label.get_text())
                                           ))
		self.label.set_attributes(att)

	def set_document(self, document):
		if self.document == document:
			return
		if self.document :
			for (key,connect) in self.signalConnections.items():
				self.document.disconnect(connect)
			self.signalConnections = {}
		self.document = document
		self.textview.set_buffer(document)
		if document.get_path():
			self.label.set_text(document.get_path())
		else:
			self.label.set_text(document.get_title())
		self.signalConnections['path-changed'] = self.document.connect('path-changed', self.on_path_changed)
		self.signalConnections['changed'] = self.document.connect('changed', self.set_bold, True)
		self.signalConnections['file-saved'] = self.document.connect('file-saved', self.set_bold, False)
		

