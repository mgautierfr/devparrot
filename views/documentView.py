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
from views.viewContainer import BaseContainer

class DocumentView(gtk.Frame):
	def __init__(self, document):
		gtk.Frame.__init__(self)
		self.document = document
		self.set_label_align(0.0, 0.0)
		self.currentView= None
		self.parentContainer = None
		
		self.label = gtk.Label()
		self.label.set_selectable(True)
		self.label.set_alignment(0, 0.5)
		self.label.props.can_focus = False
		self.set_label_widget(self.label)
		
		self.document.connect('documentSource-changed', self.on_documentSource_changed)
		self.document.connect('modified-changed', self.on_modified_changed)
		self.connect('set-focus-child', self.on_set_focus_child)
		self.connect("grab-focus", self.on_grab_focus)
		
		self.label.drag_source_set(gtk.gdk.BUTTON1_MASK, [('documentView',gtk.TARGET_SAME_APP,5)], gtk.gdk.ACTION_COPY)
		self.label.connect('drag-begin',self.on_drag_begin)
		self.label.connect('drag-data-get',self.on_drag_data_get)
		self.label.connect('drag-end',self.on_drag_end)
		
	def get_parentContainer(self) : return self.parentContainer
	def set_parentContainer(self, parent) : self.parentContainer = parent
		
		
	def set_view(self, child):
		self.add(child.container)
		self.currentView = child
		self.show_all()
	
	def on_documentSource_changed(self, documentSource, userData=None):
		self.label.set_text(self.document.longTitle)

	def on_modified_changed(self, source, buffer):
		self.set_bold(buffer.get_modified())

	def set_bold(self, bold):
		att = pango.AttrList()
		att.insert(pango.AttrWeight(pango.WEIGHT_BOLD if bold else pango.WEIGHT_NORMAL,
		                            start_index=0,
		                            end_index=len(self.label.get_text())
                                           ))
		self.label.set_attributes(att)

	def is_displayed(self):
		return self.parentContainer != None
		
	def on_grab_focus(self, widget):
		self.currentView.grab_focus()
		self.show_all()

		
	def on_set_focus_child(self, container, widget):
		if widget:
			BaseContainer.current = self.parentContainer
	
	def on_drag_begin(self, widget, drag_context, data=None):
		import core.controler
		core.controler.currentSession.get_workspace().prepare_to_dnd(True,self)
	
	def on_drag_data_get(self, widget, drag_context, selection_data, info, time, data=None):
		selection_data.set('documentView', info, self.document.longTitle)
		
	def on_drag_end(self, widget, drag_context, data=None):
		import core.controler
		core.controler.currentSession.get_workspace().prepare_to_dnd(False)
	
