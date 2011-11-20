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

import core.config
import ttk

import core.mainWindow

class TextView():
	def __init__(self, document):
		self.uiContainer = ttk.Frame(core.mainWindow.workspaceContainer)
		self.HScrollbar = ttk.Scrollbar(core.mainWindow.workspaceContainer,orient=ttk.Tkinter.HORIZONTAL)
		self.VScrollbar = ttk.Scrollbar(core.mainWindow.workspaceContainer,orient=ttk.Tkinter.VERTICAL)
		
		self.HScrollbar.grid(column=0, row=1, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
		self.VScrollbar.grid(column=1, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
		self.uiContainer.columnconfigure(0, weight=1)
		self.uiContainer.columnconfigure(1, weight=0)
		self.uiContainer.rowconfigure(0, weight=1)
		self.uiContainer.rowconfigure(1, weight=0)
		
		self.document = document

	def clone(self):
		new = TextView(self.document)
		self.document.add_view('text', new)
		return new
		
	def focus(self):
		return self.view.focus()

	def get_document(self):
		return self.document

	def set_model(self, model):
		self.view = model
		self.view['yscrollcommand'] = self.VScrollbar.set
		self.view['xscrollcommand'] = self.HScrollbar.set
		self.VScrollbar['command'] = self.view.yview
		self.HScrollbar['command'] = self.view.xview
		self.view.grid(column=0, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
		self.view.lift(self.uiContainer)
		self.view.bind('<FocusIn>', self.document.documentView.on_focus_child)
		#self.view.set_auto_indent(core.config.getboolean('textView','auto_indent'))
		#self.view.set_tab_width(core.config.getint('textView','tab_width'))
		#self.view.set_draw_spaces(core.config.getint('textView','draw_spaces'))
		#self.view.set_insert_spaces_instead_of_tabs(core.config.getboolean('textView','space_indent'))
		#self.view.set_highlight_current_line(core.config.getboolean('textView','highlight_current_line'))
		#self.view.set_show_line_numbers(core.config.getboolean('textView','show_line_numbers'))
		#self.view.set_smart_home_end(core.config.getboolean('textView','smart_home_end'))
		#self.view.modify_font(pango.FontDescription(core.config.get('textView','font')))
		#self.view.props.sensitive = True
	
	def lift(self, above):
		self.uiContainer.lift(above)
		self.VScrollbar.lift(self.uiContainer)
		self.HScrollbar.lift(self.uiContainer)
		self.view.lift(self.uiContainer)
	
	def get_context(self):
		had = self.view.get_hadjustment()
		vad = self.view.get_vadjustment()
		hadjustment = (had.value-had.lower)/(had.upper-had.lower)
		vadjustment = (vad.value-vad.lower)/(vad.upper-vad.lower)
		return (hadjustment,vadjustment)

	def set_context(self, ctx):
		had = self.view.get_hadjustment()
		vad = self.view.get_vadjustment()
		had.set_value(ctx[0]*(had.upper-had.lower)+had.lower)
		vad.set_value(ctx[1]*(vad.upper-vad.lower)+vad.lower)
		return False

