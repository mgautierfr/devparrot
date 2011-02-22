
import gtk,pango,glib
import gtksourceview2

class TextView(gtk.Frame):
	current = None
	def __init__(self):
		gtk.Frame.__init__(self)
		self.document = None
		self.parentContainer = None 

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
		
		self.connect("set-focus-child", self.on_set_focus_child)
		self.connect("grab-focus", self.on_grab_focus)
		
	def clone(self):
		new = TextView()
		new.set_document(self.document)
		return new
		
	def on_set_focus_child(self, container, widget):
		if widget:
			TextView.current = container
			
	def on_grab_focus(self, widget):
		self.textview.grab_focus()

	def get_document(self):
		return self.document
		
	def get_parentContainer(self):
		return self.parentContainer
		
	def set_parentContainer(self, container):
		self.parentContainer = container

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

	def start_search(self, text):
		if not self.document: return
		foundIter = self.document.start_search(text)
		if foundIter:
			self.textview.scroll_to_iter(foundIter, 0.2)

	def next_search(self):
		if not self.document: return
		foundIter = self.document.next_search()
		if foundIter:
			self.textview.scroll_to_iter(foundIter, 0.2)

	def goto_line(self, line):
		def callback(it):
			self.textview.scroll_to_iter(it, 0.2)
			return False
		line_iter = self.document.get_iter_at_line(line)
		self.document.select_range(line_iter,line_iter)
		glib.idle_add(callback, line_iter)

