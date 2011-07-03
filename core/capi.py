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


import controler, mainWindow
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
		return controler.currentSession.get_documentManager().__len__()
	
	def __getitem__(self, key):
		return controler.currentSession.get_documentManager().__getitem__(key)[0]
			
def __getattr__(name):
	if name == 'currentDocument':
		return controler.currentSession.get_currentDocument()
	if name == 'currentContainer':
		return controler.currentSession.get_workspace().get_currentContainer()
	raise AttributeError

def __setattr__(name, value):
	if name == 'currentDocument':
		if value.documentView.is_displayed():
			value.documentView.grab_focus()
		else:
			__getattr__('currentContainer').set_documentView(value.documentView)
		return
	raise AttributeError

def add_file(document):
	return controler.currentSession.get_documentManager().add_file(document)

def file_is_opened(filePath):
	return controler.currentSession.get_documentManager().has_file(filePath)

def get_file(filePath):
	return controler.currentSession.get_documentManager().get_file(filePath)
	
def get_nth_file(index):
	docManager = controler.currentSession.get_documentManager()
	return docManager.get_value(docManager.get_iter(str(index)), 0) 

def del_file(document):
	controler.currentSession.get_documentManager().del_file(document)

def ask_for_filename_to_save(title):
	return mainWindow.Helper().ask_filenameSave(title=title)
	
def ask_for_filename_to_open(title, defaultDir):
	return mainWindow.Helper().ask_filenameOpen(title=title, currentFolder=defaultDir)

def quit():
	import gtk
	gtk.main_quit()

sys.modules[__name__] = ModuleWrapper(sys.modules[__name__])
documents = DocumentWrapper()
