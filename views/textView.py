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

import gtk,pango,glib
import gtksourceview2

class TextView(gtksourceview2.View):
	def __init__(self):
		gtksourceview2.View.__init__(self)
		self.set_auto_indent(True)
		self.set_highlight_current_line(True)
		self.set_show_line_numbers(True)
		self.set_smart_home_end(True)
		self.modify_font(pango.FontDescription("monospace"))
		self.props.sensitive = False

		self.connect('focus-in-event',self.on_focus_in_event)

		self.document = None
		self.parentContainer = None

		self.label = gtk.Label()
		self.label.set_selectable(True)
		self.label.set_alignment(0, 0.5)
		self.label.props.can_focus = False

		self.signalConnections = {}

	def clone(self):
		new = TextView()
		new.set_document(self.document)
		return new

	def on_focus_in_event(self, widget, event):
		res = self.document.check_for_exteriorModification()
		if res == None : return
		if res:
			import mainWindow
			answer = mainWindow.Helper().ask_questionYesNo("File content changed",
			                                                                                      "The content of file %s has changed.\nDo you want to reload it?"%self.document.get_title())
			if answer:
				self.document.load()
			else:
				self.document.init_timestamp()

	def get_titleWidget(self):
		return self.label

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

	def on_modified_changed(self, buffer):
		self.set_bold(buffer.get_modified())

	def set_bold(self, bold):
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
			for (key,(obj,connect)) in self.signalConnections.items():
				obj.disconnect(connect)
			self.signalConnections = {}
		self.document = document
		if self.document:
			self.set_buffer(document.get_model("text"))
			self.props.sensitive = True
			if document.get_path():
				self.label.set_text(document.get_path())
			else:
				self.label.set_text(document.get_title())
			self.set_bold( self.get_buffer().get_modified())
			self.signalConnections['path-changed'] = (self.document, self.document.connect('path-changed', self.on_path_changed) )
			self.signalConnections['modified-changed'] = (self.get_buffer(), self.get_buffer().connect('modified-changed', self.on_modified_changed) )
		else:
			self.set_buffer(gtk.TextBuffer())
			self.props.sensitive = False
			self.label.set_text("")
			self.set_bold(False)

	def search(self, backward, text):
		if not self.document: return
		foundIter = self.get_buffer().search(backward,text)
		if foundIter:
			self.scroll_to_iter(foundIter, 0.2)

	def goto_line(self, line, delta = None):
		def callback(it):
			self.scroll_to_iter(it, 0.2)
			return False
		if delta != None:
			current_line = self.get_buffer().get_iter_at_mark(self.get_buffer().get_insert()).get_line()
			if delta == '+':
				line = current_line + line
			if delta == '-':
				line = current_line - line
		line_iter = self.get_buffer().get_iter_at_line(line)
		self.get_buffer().select_range(line_iter,line_iter)
		glib.idle_add(callback, line_iter)