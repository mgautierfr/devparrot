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

from actionDef import Action

import gtk
import os

import controler, mainWindow

def save_document(document, fileToSave=None):
	if not document: return False
	if document.get_path() and not fileToSave:
		document.write()
		return True
	if not document.get_path() and not fileToSave:
		fileToSave = mainWindow.Helper().ask_filenameSave("Save")

	if not fileToSave:
		return False

	(newDocument, newOne) = controler.currentSession.get_documentManager().get_file(fileToSave, False)
	if newDocument:
		# If the document is already opened change its content and delete the older one
		document.get_model('text').save_to_document(newDocument)
		newDocument.load()
		controler.currentSession.get_workspace().set_currentDocument(newDocument)
		controler.currentSession.get_documentManager().del_file(document)
	else:
		document.set_path(fileToSave)
		document.write()

	return True


class save(Action):
	accelerators=[gtk.accelerator_parse("<Control>s")]


	def run(cls, args=[]):
		if len(args)>=1:
			return save_document(controler.currentSession.get_currentDocument(),os.path.abspath(args[0]))
		else:
			return save_document(controler.currentSession.get_currentDocument(), None)


class new(Action):
	accelerators=[gtk.accelerator_parse("<Control>n")]
	def run(cls, args=[]):
		f = controler.currentSession.get_documentManager().new_file()
		controler.currentSession.get_workspace().set_currentDocument(f)

def switch(Action):
	def run(cls, args=[]):
		if len(args)==0:
			return False
		path = args[0]
		docManager = controler.currentSession.get_documentManager()
		document = docManager.get_value(docManager.get_iter(path), 0)
		controler.currentSession.get_workspace().set_currentDocument(document)
	
	
def close_document(document):
	docManager = controler.currentSession.get_documentManager()
	if document.check_for_save():
			save_document(document)
	docManager.del_file(document)
	if document == controler.currentSession.get_workspace().get_currentDocument():
		docToDisplay = None
		try :
			docToDisplay = docManager.get_value(docManager.get_iter("0"), 0)
		except ValueError:
			pass
		controler.currentSession.get_workspace().set_currentDocument(docToDisplay)
		
		
class close(Action):
	def run(cls, args=[]):
		docManager = controler.currentSession.get_documentManager()
		if len(args)==0 or not args[0]:
			document = controler.currentSession.get_currentDocument()
		else:
			path = args[0]
			document = docManager.get_value(docManager.get_iter(path), 0)
		close_document(document)

class debug(Action):
	def run(cls, args=[]):
		print controler.currentSession.get_documentManager()

class open(Action):
	accelerators=[gtk.accelerator_parse("<Control>o")]

	def open_a_file(cls, fileToOpen):
		if not fileToOpen: return
		lineToGo = None
		# if path doesn't exist and we have a line marker, lets go to that line
		if not os.path.exists(fileToOpen):
			parts = fileToOpen.split(':')
			if len(parts) == 2:
				fileToOpen = parts[0]
				try :
					lineToGo= int(parts[1])
				except: pass
		(doc, newOne) = controler.currentSession.get_documentManager().get_file(fileToOpen)
		if newOne:
			doc.load()
		controler.currentSession.get_workspace().set_currentDocument(doc)
		if lineToGo:
			controler.currentSession.get_workspace().get_currentView().goto_line(lineToGo-1)

	def run(cls, args=[]):
		if len(args)>=1:
			for fileToOpen in args:
				cls.open_a_file(fileToOpen)
		else:
			path = None
			currentDoc = controler.currentSession.get_workspace().get_currentDocument()
			if currentDoc:
				path = currentDoc.get_path()
				if path: path = os.path.dirname(path)
			fileToOpen = mainWindow.Helper().ask_filenameOpen("Open a file", path)
			cls.open_a_file(fileToOpen)

class quit(Action):
	def run(cls, args=[]):
		import gtk
		closeall()
		gtk.main_quit()
	
class closeall(Action):
	def run(cls, args=[]):
		docManager = controler.currentSession.get_documentManager()
		for (doc, ) in docManager:
			close_document(doc)

class split(Action):
	from views.viewContainer import ViewContainer
	SPLIT = 0
	UNSPLIT = 1

	def regChecker(cls, line):
		if line.startswith("split"):
			return [cls.SPLIT, cls.ViewContainer.Horizontal]
		if line.startswith("vsplit"):
			return [cls.SPLIT, cls.ViewContainer.Vertical]
		if line.startswith("unsplit"):
			return [cls.UNSPLIT]
		return None

	def run(cls, args=[]):
		if args[0] == cls.SPLIT:
			controler.currentSession.get_workspace().get_currentViewContainer().split(args[1])
		if args[0] == cls.UNSPLIT:
			controler.currentSession.get_workspace().get_currentViewContainer().unsplit()

class search(Action):
	accelerators=[gtk.accelerator_parse("F3")]
	import re
	lastSearch = None
	FORWARD=False
	BACKWARD=True

	def regChecker(cls, line):
		import re
		if line.startswith("search"):
			ret = [cls.FORWARD]
			ret.extend(line.split(' ')[1:])
			return ret
		if line.startswith("next"):
			return []
		match = re.match(r"^/(.*)$", line)
		if match:
			ret = [cls.FORWARD]
			ret.extend(match.groups())
			return ret
		match = re.match(r"^\?(.*)$", line)
		if match:
			ret = [cls.BACKWARD]
			ret.extend(match.groups())
			return  ret
		return None

	def run(cls, args=[]):
		if len(args):
			cls.lastSearch = args
			return controler.currentSession.get_workspace().get_currentView().search(*args)
		if cls.lastSearch:
			return controler.currentSession.get_workspace().get_currentView().search(*cls.lastSearch)

class goto(Action):
	def run(cls, args=[]):
		if len(args) and args[0]:
			try :
				line = int(args[0])
				controler.currentSession.get_workspace().get_currentView().goto_line(line-1)
			except:
				pass
