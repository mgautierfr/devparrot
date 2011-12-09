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

import Tkinter,ttk,Tkdnd
from views.viewContainer import LeafSpecialization,AbstractContainerChild

import core.mainWindow

class DocumentView(ttk.Frame,AbstractContainerChild):
	def __init__(self, document):
		ttk.Frame.__init__(self,core.mainWindow.workspaceContainer, padding=0, relief="flat", borderwidth=0)
		AbstractContainerChild.__init__(self)
		self.document = document
		self.currentView= None
		
		import tkFont
		self.label = ttk.Label(self)
		self.label.font = tkFont.Font(font="TkDefaultFont")
		self.label['textvariable'] = document.titleVar
		self.label['font'] = self.label.font
		self.label.pack()

		self.bind('<FocusIn>', self.on_focus)
		
		self.label.bind_class("Drag","<Button-1><Button1-Motion>", self.on_drag_begin)
		self.label.bindtags(" ".join(["Drag"]+[t for t in self.label.bindtags()]))
		
	def set_view(self, child):
		child.uiContainer.pack(in_=self, expand=True, fill=ttk.Tkinter.BOTH)
		self.currentView = child
	
	def lift(self):
		ttk.Frame.lift(self, self.parentContainer.uiContainer)
		if self.currentView != None: 
			self.currentView.lift(self)
	
	def on_modified(self, varname, value, mode):
		var = ttk.Tkinter.BooleanVar(name=varname)
		self.set_bold(var.get())		
		return False

	def set_bold(self, bold):
		self.label.font['weight'] = "bold" if bold else "normal"

	def is_displayed(self):
		return self.parentContainer != None
		
	def on_focus(self, event):
		self.currentView.focus()

	def on_focus_child(self, event):
		LeafSpecialization.current = self.parentContainer
	
	def on_drag_begin(self, event):
		event.num = 1
		Tkdnd.dnd_start(self, event)
		
	def dnd_end(self, target, event):
		print "ending drag"	
	
