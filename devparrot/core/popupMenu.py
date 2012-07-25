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
import commandLauncher


class Menu(ttk.Tkinter.Menu):
	def __init__(self):
		ttk.Tkinter.Menu.__init__(self)
		self.sections = []
		self.config(postcommand=self.postCommand)
		self.add_section(EditSection(self))
		self.createMenu()
		pass
	
	def add_section(self, section):
		self.sections.append(section)
	
	def createMenu(self):
		for section in self.sections:
			section.createMenu()
	
	def postCommand(self):
		for section in self.sections:
			section.postCommand()
		
class EditSection:
	def __init__(self, menu):
		self.menu = menu
	
	def createMenu(self):
		self.menu.add_command(label='Undo', command=lambda:commandLauncher.run_command('undo\n'))
		self.menu.add_command(label='Redo', command=lambda:commandLauncher.run_command('redo\n'))
		self.menu.add_separator()
		self.menu.add_command(label='Copy',  command=lambda:commandLauncher.run_command('copy\n'))
		self.menu.add_command(label='Cut',   command=lambda:commandLauncher.run_command('cut\n'))
		self.menu.add_command(label='Paste', command=lambda:commandLauncher.run_command('paste\n'))
	
	def postCommand(self):
		try:
			self.menu.clipboard_get()
			self.menu.entryconfigure('Paste', state="normal")
		except:
			self.menu.entryconfigure('Paste', state="disable")

		import command.capi
		try:
			core.command.capi.currentDocument.get_currentView().view.index('sel.first')
			core.command.capi.currentDocument.get_currentView().view.index('sel.last')
			self.menu.entryconfigure('Cut', state="normal")
			self.menu.entryconfigure('Copy', state="normal")
		except:
			self.menu.entryconfigure('Cut', state="disable")
			self.menu.entryconfigure('Copy', state="disable")