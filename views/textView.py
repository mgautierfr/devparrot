
import gtk,pango
import gtksourceview2

class TextView(gtk.Frame):
	def __init__(self):
		gtk.Frame.__init__(self)
		self.document = None 

		self.label = gtk.Label()
		self.label.set_selectable(True)
		self.label.set_alignment(0, 0.5)
		self.label.props.can_focus = False
		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.textview = gtksourceview2.View()
		self.textview.set_auto_indent(True)
		self.textview.set_highlight_current_line(True)
		self.textview.set_show_line_numbers(True)
		self.textview.set_smart_home_end(True)
		self.scrolledwindow.add(self.textview)
		self.add(self.scrolledwindow)
		self.set_label_widget(self.label)
		self.set_label_align(0.0,0.0)

		self.show_all()
		self.props.sensitive = False

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
		if self.document and document and self.document == document:
			return
		if self.document :
			for (key,connect) in self.signalConnections.items():
				self.document.disconnect(connect)
			self.signalConnections = {}
		self.document = document
		if self.document:
			self.textview.set_buffer(document)
			self.props.sensitive = True
			if document.get_path():
				self.label.set_text(document.get_path())
			else:
				self.label.set_text(document.get_title())
			self.set_bold(None, document.get_modified())
			self.signalConnections['path-changed'] = self.document.connect('path-changed', self.on_path_changed)
			self.signalConnections['changed'] = self.document.connect('changed', self.set_bold, True)
			self.signalConnections['file-saved'] = self.document.connect('file-saved', self.set_bold, False)
		else:
			self.textview.set_buffer(gtk.TextBuffer())
			self.props.sensitive = False
			self.label.set_text("")
			self.set_bold(None, False)

