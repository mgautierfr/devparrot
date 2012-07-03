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
		self.HScrollbar.grid(column=0,
		                     row=1,
		                     columnspan=10,
		                     in_=self.uiContainer,
		                     sticky="nsew"
		                    )

		self.VScrollbar = ttk.Scrollbar(core.mainWindow.workspaceContainer,orient=ttk.Tkinter.VERTICAL)	
		self.VScrollbar.grid(column=10, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))

		self.lineNumbers = ttk.Tkinter.Canvas(core.mainWindow.workspaceContainer,
		                                      highlightthickness = 0,
		                                      takefocus = 0,
		                                      bd=0,
		                                      background = 'lightgrey',
		                                      state='disable',
		                                     )
		self.lineNumbers.grid(column=0, row=0, in_=self.uiContainer, sticky="nsw")

		self.uiContainer.columnconfigure(0, weight=0)
		self.uiContainer.columnconfigure(1, weight=1)
		self.uiContainer.columnconfigure(10, weight=0)
		self.uiContainer.rowconfigure(0, weight=1)
		self.uiContainer.rowconfigure(1, weight=0)
		
		self.VScrollbar['command'] = self.proxy_yview

		self.document = document
		
		self.firstLine = 1
		self.lastLine = 1
		self.lastLineCreated = 0
		self.actualLineNumberWidth = 0

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

	def _create_textLine(self, name):
		self.lineNumbers.create_text("0","0", anchor="nw", text=name, tags=name, state="hidden")
		
	def set_lineNumbers(self):
		self.lineNumbers.config(state='normal')
		
		nbLine = int(self.view.index('end').split('.')[0])
		if self.lastLineCreated < nbLine:
			[self._create_textLine('%d'%(i+1)) for i in range(self.lastLineCreated, nbLine)]
			self.lastLineCreated = nbLine
		
		firstLine = int(self.view.index('@0,0').split('.')[0])-1
		lastLine = int(self.view.index('@0,%d'%self.view.winfo_height()).split('.')[0])+1
		
		firstLine = max(firstLine, 1)
		lastLine = min(lastLine, nbLine)

		for i in range( min(firstLine,self.firstLine) , max(lastLine, self.lastLine)+1 ):
			name = "%d"%i
			pos = self.view.bbox("%d.0"%i)
			if pos:
				self.lineNumbers.coords(name, "0", "%d"%pos[1])
				self.lineNumbers.itemconfig(name, state="disable")
			else:
				self.lineNumbers.itemconfig(name, state="hidden")

		self.firstLine = firstLine
		self.lastLine = lastLine

		bbox = self.lineNumbers.bbox('all')
		if bbox:
			w = int(bbox[2])
			if self.actualLineNumberWidth < w:
				self.actualLineNumberWidth = w
				self.lineNumbers.config(width=self.actualLineNumberWidth)

		self.lineNumbers.config(state='disable')
	
	def on_event_lineChanged(self, *args):
		self.set_lineNumbers()


	def set_model(self, model):
		self.view = model
		self.view['yscrollcommand'] = self.proxy_yscrollcommand
		self.view['xscrollcommand'] = self.HScrollbar.set
		self.HScrollbar['command'] = self.view.xview
		self.view.grid(column=1, row=0, in_=self.uiContainer, sticky=(ttk.Tkinter.N, ttk.Tkinter.S, ttk.Tkinter.E, ttk.Tkinter.W))
		self.view.lift(self.uiContainer)
		self.view.bind('<FocusIn>', self.document.documentView.on_focus_child)
		self.view.connect('insert', self.on_event_lineChanged)
		self.view.connect('delete', self.on_event_lineChanged)

	
		#self.view.set_auto_indent(core.config.getboolean('textView','auto_indent'))
		#self.view.set_tab_width(core.config.getint('textView','tab_width'))
		#self.view.set_draw_spaces(core.config.getint('textView','draw_spaces'))
		#self.view.set_insert_spaces_instead_of_tabs(core.config.getboolean('textView','space_indent'))
		#self.view.set_highlight_current_line(core.config.getboolean('textView','highlight_current_line'))
		#self.view.set_show_line_numbers(core.config.getboolean('textView','show_line_numbers'))
		#self.view.set_smart_home_end(core.config.getboolean('textView','smart_home_end'))
		#self.view.props.sensitive = True
	
	def copy_clipboard(self):
		if self.view:
			try:
				self.view.clipboard_clear()
				self.view.clipboard_append(self.view.get('sel.first','sel.last'))
			except:
				# there is no selection, can't copy
				return False
			return True

	def cut_clipboard(self):
		if self.view:
			try:
				self.view.clipboard_clear()
				self.view.clipboard_append( self.view.get( 'sel.first', 'sel.last' ) )
				self.view.delete( 'sel.first', 'sel.last' )
				self.view.sel_clear( )
			except:
				# there is no selection, can't cut
				return False
			return True

	def paste_clipboard(self):
		if self.view:
			try:
				self.view.mark_set( 'insert', 'sel.first' )
				self.view.delete( 'sel.first', 'sel.last' )
			except:
				# not a pb if there is no selection
				pass
			self.view.insert( 'insert', self.view.clipboard_get( ) )
			self.view.sel_clear( )
			return True

	def lift(self, above):
		self.uiContainer.lift(above)
		self.VScrollbar.lift(self.uiContainer)
		self.HScrollbar.lift(self.uiContainer)
		ttk.Tkinter.Misc.lift(self.lineNumbers, aboveThis=self.uiContainer)
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
