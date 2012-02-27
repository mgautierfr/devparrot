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
		self.HScrollbar.grid(column=0, row=1, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))

		self.VScrollbar = ttk.Scrollbar(core.mainWindow.workspaceContainer,orient=ttk.Tkinter.VERTICAL)	
		self.VScrollbar.grid(column=10, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))

		self.lineNumbers = ttk.Tkinter.Canvas(core.mainWindow.workspaceContainer,
		                                      width = 4,
		                                      highlightthickness = 0,
		                                      takefocus = 0,
		                                      bd=0,
		                                      background = 'lightgrey',
		                                      state='disable',
		                                     )
		self.lineNumbers.grid(column=0, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))

		self.uiContainer.columnconfigure(0, weight=0)
		self.uiContainer.columnconfigure(1, weight=1)
		self.uiContainer.columnconfigure(10, weight=0)
		self.uiContainer.rowconfigure(0, weight=1)
		self.uiContainer.rowconfigure(1, weight=0)
		
		self.VScrollbar['command'] = self.proxy_yview

		self.document = document

		self.lastLine = 0

	def clone(self):
		new = TextView(self.document)
		self.document.add_view('text', new)
		return new
		
	def focus(self):
		return self.view.focus()

	def get_document(self):
		return self.document

	def proxy_yview(self, *args, **kwords):
		if self.view:
			self.view.yview(*args, **kwords)
			self.set_lineNumbers()

	def proxy_yscrollcommand(self, *args, **kwords):
		self.VScrollbar.set(*args, **kwords)
		self.set_lineNumbers()

	def set_lineNumbers(self):
		end = self.view.index('end')
		ln, cn = end.split('.')
		self.lineNumbers.config(state='normal')
		for i in range(1, int(ln)):
			if i >= self.lastLine:
				self.lineNumbers.create_text("0","0", anchor="nw", text="%d"%i, tags=["%d"%i], state="hidden")
				self.lastLine += 1
			pos = self.view.bbox("%d.0"%i)
			if pos:
				self.lineNumbers.itemconfig("%d"%i, state="disable")
				self.lineNumbers.coords("%d"%i, "0", "%d"%pos[1])
			else:
				self.lineNumbers.itemconfig("%d"%i, state="hidden")
		for i in range(int(ln), self.lastLine):
			self.lineNumbers.itemconfig("%d"%i, state="hidden")
		
		self.lineNumbers.config(state='disable')


	def set_model(self, model):
		self.view = model
		self.view['yscrollcommand'] = self.proxy_yscrollcommand
		self.view['xscrollcommand'] = self.HScrollbar.set
		self.HScrollbar['command'] = self.view.xview
		self.view.grid(column=1, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
		self.view.lift(self.uiContainer)
		self.view.bind('<FocusIn>', self.document.documentView.on_focus_child)

	
		#self.view.set_auto_indent(core.config.getboolean('textView','auto_indent'))
		#self.view.set_tab_width(core.config.getint('textView','tab_width'))
		#self.view.set_draw_spaces(core.config.getint('textView','draw_spaces'))
		#self.view.set_insert_spaces_instead_of_tabs(core.config.getboolean('textView','space_indent'))
		#self.view.set_highlight_current_line(core.config.getboolean('textView','highlight_current_line'))
		#self.view.set_show_line_numbers(core.config.getboolean('textView','show_line_numbers'))
		#self.view.set_smart_home_end(core.config.getboolean('textView','smart_home_end'))
		#self.view.props.sensitive = True
	
	def lift(self, above):
		self.uiContainer.lift(above)
		self.VScrollbar.lift(self.uiContainer)
		self.HScrollbar.lift(self.uiContainer)
		self.lineNumbers.lift(self.uiContainer)
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



