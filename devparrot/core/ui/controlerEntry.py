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

import Tkinter
from devparrot.core import commandLauncher

class ControlerEntry(Tkinter.Text):
	def __init__(self, parent):
		Tkinter.Text.__init__(self, parent, height=1)
		self.toClean = False
		
		
		
		self.bind('<FocusIn>', self.on_get_focus)
		self.bind('<FocusOut>', self.on_lost_focus)
		self.bind('<Key>', self.on_entry_event)

		self.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.toplevel = Tkinter.Toplevel()
		self.toplevel.bind('<FocusOut>', self.on_lost_focus)
		self.display_list(False)
		self.toplevel.wm_overrideredirect(True)

		self.listbox = Tkinter.Listbox(self.toplevel)
		self.listbox.place(relwidth=1.0, relheight=1.0)
		self.listbox.bind('<Key>', self.on_listbox_event)
		self.bind('<Control-Return>', lambda e: "continue")
		
		self.bind("<<Modified>>", self.on_textChanged)

		bindtags = list(self.bindtags())
		bindtags.insert(1,"Command")
		bindtags = " ".join(bindtags)
		self.bindtags(bindtags)

	def display_list(self, display):
		self.displayed = display
		if display:
			self.set_position()
			self.toplevel.deiconify()
		else:
			self.toplevel.withdraw()

	def set_position(self):
		xroot = self.winfo_rootx()
		yroot = self.winfo_rooty()+self.winfo_height()
		self.toplevel.wm_geometry("+%d+%d"% (xroot, yroot))
		self.toplevel.minsize(width=self.winfo_width(), height=0)

	def on_lost_focus(self, event):
		focused = self.focus_get()
		if focused not in (self, self.toplevel, self.listbox):
			self.display_list(False)
	
	def on_entry_event(self, event):
		if event.keysym == 'Up':
			self.delete("1.0", "end")
			self.insert("end", commandLauncher.currentSession.get_history().get_previous())
		if event.keysym == "Down":
			next = commandLauncher.currentSession.get_history().get_next()
			if next:
				self.delete("1.0", "end")
				self.insert("end", commandLauncher.currentSession.get_history().get_next())
			else:
				self.display_list(True)
				self.listbox.focus()
				self.listbox.select_set(0)
			return
		if event.keysym == 'Tab':
			startIndex = self.startIndex
			toInsert = self.commonString
			self.delete(startIndex, 'insert')
			self.insert(startIndex, toInsert)
			self.mark_set("insert", startIndex+" + %dc"%len(toInsert))
			self.display_list(True)
			self.listbox.focus()
			self.listbox.select_set(0)
			return "break"
		if event.keysym == 'Return':
			from devparrot.core import config
			self.display_list(False)
			text = self.get("1.0", "end")
			ret = commandLauncher.run_command(text)
			if ret is None:
				self.configure(background=config.color.notFoundColor)
			elif ret:
				self.configure(background=config.color.okColor)
				self.toClean = True
			else:
				self.configure(background=config.color.errorColor)
			if commandLauncher.currentSession.get_workspace().get_currentDocument():
				commandLauncher.currentSession.get_workspace().get_currentDocument().get_currentView().focus()
			return "break"
		if event.keysym == 'Escape':
			self.display_list(False)
			if commandLauncher.currentSession.get_workspace().get_currentDocument():
				commandLauncher.currentSession.get_workspace().get_currentDocument().get_currentView().focus()
			return
	
	def on_listbox_event(self, event):
		from pyparsing import printables
		if event.keysym == 'Escape':
			self.display_list(False)
			self.focus()
			return
		if event.keysym == 'Return':
			self.display_list(False)
			try:
				completion = str(self.completions[int(self.listbox.curselection()[0])])
				startIndex = self.startIndex
				self.delete(startIndex, 'insert')
				self.insert(startIndex, completion)
				self.mark_set("index", startIndex + "+ %dc"%len(completion))
				self.focus()
			except:
				pass
			return
		if event.keysym == 'Tab':
			try:
				startIndex = self.startIndex
				toInsert = self.commonString or str(self.completions[int(self.listbox.curselection()[0])])
				self.delete(startIndex, 'insert')
				self.insert(startIndex, toInsert)
				self.mark_set("index", startIndex + "+ %dc"%len(toInsert))
			except:
				pass
			return
		if event.keysym == 'Left':
			self.mark_set("index", "index - 1c")
			self.update_completion()
			return
		if event.keysym == 'Right':
			self.mark_set("index", "index + 1c")
			self.update_completion()
			return
		if event.keysym == 'BackSpace':
			self.delete(self.index('insert')-1)
			self.update_completion()
			return
		char = event.char.decode('utf8')
		if char and char in printables:
			self.insert('insert', event.char)
			self.focus()
	
	def update_completion(self):
		self.startIndex, self.commonString, self.completions = commandLauncher.get_completions(self.get("1.0", "insert"))
		self.startIndex = "1.%d"%self.startIndex
		self.listbox.delete('0', 'end')
		for v in self.completions:
			self.listbox.insert('end', v.value)

	def on_textChanged(self, *args):
		self.update_completion()
		self.edit_modified(False)
		
	def on_get_focus(self, event):
		if self.toClean:
			self.toClean = False
			self.configure(background="white")
			self.delete("1.0",'end')
