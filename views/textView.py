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

class TextView():
	def __init__(self, document):
		self.container = gtk.ScrolledWindow()
		self.view = gtksourceview2.View()
		
		self.container.add(self.view)
		self.container.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		
		self.view.set_auto_indent(True)
		self.view.set_highlight_current_line(True)
		self.view.set_show_line_numbers(True)
		self.view.set_smart_home_end(True)
		self.view.modify_font(pango.FontDescription("monospace"))
		self.view.props.sensitive = False
		self.document = document

	def clone(self):
		new = TextView(self.document)
		self.document.add_view('text', new)
		return new
		
	def grab_focus(self):
		return self.view.grab_focus()

	def get_document(self):
		return self.document

	def get_parentContainer(self):
		return self.parentContainer

	def set_parentContainer(self, container):
		self.parentContainer = container

	def set_model(self, model):
		self.view.set_buffer(model)
		self.view.props.sensitive = True