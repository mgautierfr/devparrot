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

import ttk
from devparrot.core import commandLauncher

class ControlerEntry(ttk.Entry):
	def __init__(self, parent):
		self.textVariable = ttk.Tkinter.StringVar()
		ttk.Entry.__init__(self, parent, textvariable=self.textVariable)
		self.toClean = False
		
		
		
		self.bind('<FocusIn>', self.on_get_focus)
		self.bind('<Key>', self.on_entry_event)
		
		self.pack(side=ttk.Tkinter.TOP, fill=ttk.Tkinter.X)
		self.toplevel = ttk.Tkinter.Toplevel()
		self.toplevel.withdraw()
		self.toplevel.wm_overrideredirect(True)
		self.listbox = ttk.Tkinter.Listbox(self.toplevel)
		self.listbox.place(relwidth=1.0, relheight=1.0)
		self.listbox.bind('<Key>', self.on_listbox_event)
		
		self.textVariable.trace('w', self.on_textChanged)
		self.on_textChanged()
		
	def set_position(self):
		xroot = self.winfo_rootx()
		yroot = self.winfo_rooty()+self.winfo_height()
		self.toplevel.wm_geometry("+%d+%d"% (xroot, yroot))
		self.toplevel.minsize(width=self.winfo_width(), height=0)
		
	
	def on_entry_event(self, event):
		if event.keysym in ('Up', 'Down'):
			self.delete("0", "end")
			if event.keysym == 'Up':
				self.insert("end", commandLauncher.currentSession.get_history().get_previous())
			else:
				self.insert("end", commandLauncher.currentSession.get_history().get_next())
			return
		if event.keysym == 'Tab':
			self.set_position()
			self.toplevel.deiconify()
			self.listbox.focus()
			self.listbox.select_set(0)
			return
		if event.keysym == 'Return':
			text = self.textVariable.get()
			ret = commandLauncher.run_command(text+"\n")
			if ret is None:
				self['style'] = "notFoundStyle.TEntry"
			elif ret:
				self['style'] = "okStyle.TEntry"
				self.toClean = True
			else:
				self['style'] = "errorStyle.TEntry"
			if commandLauncher.currentSession.get_workspace().get_currentDocument():
				commandLauncher.currentSession.get_workspace().get_currentDocument().get_currentView().focus()
		if event.keysym == 'Escape':
			if commandLauncher.currentSession.get_workspace().get_currentDocument():
				commandLauncher.currentSession.get_workspace().get_currentDocument().get_currentView().focus()
			return
	
	def on_listbox_event(self, event):
		if event.keysym == 'Escape':
			self.toplevel.withdraw()
			self.focus()
			return
		if event.keysym == 'Return':
			try:
				print 'select is', self.completions[int(self.listbox.curselection()[0])]
			except:
				pass
			return
		if event.keysym == 'BackSpace':
			self.delete(self.index('insert')-1)
			return
		if len(event.char) > 0:
			self.insert('insert', event.char)
	
	def on_textChanged(self, *args):
		self.completions = commandLauncher.get_completions(self.get()[:self.index('insert')])
		self.listbox.delete('0', 'end')
		for v in self.completions:
			self.listbox.insert('end', v)
		
		
	def on_get_focus(self, event):
		if self.toClean:
			self.toClean = False
			self['style'] = ""
			self.delete(0,'end')
