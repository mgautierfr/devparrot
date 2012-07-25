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


from devparrot.core.ui import viewContainer
import sys

class ModuleWrapper(object):
	def __init__(self, module):
		self.__dict__['module'] = module
	
	def __getattr__(self, name):
		try:
			return getattr(self.module, name)
		except AttributeError:
			return self.module.__getattr__(name)
	
	def __setattr__(self, name, value):
		return self.module.__setattr__(name, value)
			
class DocumentWrapper(object):
	def __init__(self):
		pass
		
	def __len__(self):
		from devparrot.core import commandLauncher
		return commandLauncher.currentSession.get_documentManager().get_nbDocuments()
	
	def __getitem__(self, key):
		from devparrot.core import commandLauncher
		return commandLauncher.currentSession.get_documentManager().get_nthFile(key)


def __getattr__(name):
	from devparrot.core import commandLauncher
	if name == 'currentDocument':
		return commandLauncher.currentSession.get_currentDocument()
	if name == 'currentContainer':
		return commandLauncher.currentSession.get_workspace().get_currentContainer()
	if name == 'bind':
		from devparrot.core.command import binder
		return binder
	raise AttributeError

def __setattr__(name, value):
	if name == 'currentDocument':
		if value == None:
			__getattr__('currentContainer').set_documentView(None)
		elif value.documentView.is_displayed():
			value.documentView.parentContainer.select(value.documentView)
			value.documentView.focus()
		else:
			__getattr__('currentContainer').set_documentView(value.documentView)
			value.documentView.focus()

		return
	raise AttributeError

def add_file(document):
	from devparrot.core import commandLauncher
	return commandLauncher.currentSession.get_documentManager().add_file(document)

def file_is_opened(filePath):
	from devparrot.core import commandLauncher
	return commandLauncher.currentSession.get_documentManager().has_file(filePath)

def get_file(filePath):
	from devparrot.core import commandLauncher
	return commandLauncher.currentSession.get_documentManager().get_file(filePath)
	
def get_nth_file(index):
	from devparrot.core import commandLauncher
	return commandLauncher.currentSession.get_documentManager().get_nthFile(index)

def del_file(document):
	from devparrot.core import commandLauncher
	return commandLauncher.currentSession.get_documentManager().del_file(document)

def open_file(filePath):
	if file_is_opened(filePath):
		return get_file(filePath)
	from devparrot.core import document
	doc = document.Document(documents.fileDocSource.FileDocSource(filePath))
	add_file(doc)
	doc.load()
	return doc

def quit():
	from devparrot.core import ui
	def destroy():
		ui.mainWindow.window.destroy()	
	ui.mainWindow.window.after_idle(destroy)
	
def split(vertical, first=True):
	return viewContainer.split(__getattr__('currentContainer').get_documentView(), vertical, first)

def unsplit(container=None):
	if not container:
		container = __getattr__('currentContainer')
	return viewContainer.unsplit(container)

sys.modules[__name__] = ModuleWrapper(sys.modules[__name__])
documents = DocumentWrapper()
