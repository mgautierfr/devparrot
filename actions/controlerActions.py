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

from actionDef import Action, Accelerator, accelerators

import os
import capi

class save(Action):

	@accelerators(Accelerator("<Control>s"))
	def run(cls, args=[]):
		if len(args)>=1:
			return save.save_document(capi.currentDocument,os.path.abspath(args[0]))
		else:
			return save.save_document(capi.currentDocument, None)

	@staticmethod			
	def save_document(document, fileToSave=None):
		if not document: return False
		if document.has_a_path() and not fileToSave:
			document.write()
			return True
		if not document.has_a_path() and not fileToSave:
			fileToSave = capi.ask_for_filename_to_save(title="Save")

		if not fileToSave:
			return False

		newDocument = capi.get_file(fileToSave)
		if capi.file_is_opened(fileToSave):
			# If the document is already opened change its content and delete the older one
			newDocument = capi.get_file(fileToSave)
			document.get_model('text').save_to_document(newDocument)
			newDocument.load()
			capi.currentDocument = newDocument
			capi.del_file(document)
		else:
			document.set_path(fileToSave)
			document.write()

		return True


class new(Action):
	@accelerators(Accelerator("<Control>n"))
	def run(cls, args=[]):
		capi.currentDocument = capi.new_file()

class switch(Action):
	def run(cls, args=[]):
		if len(args)==0:
			return False
		path = args[0]
		capi.currentDocument = capi.get_nth_file(path)
		
		
class close(Action):
	def run(cls, args=[]):
		if len(args)==0 or not args[0]:
			document = capi.currentDocument
		else:
			path = args[0]
			document = capi.documents[path]
		close.close_document(document)

	@staticmethod		
	def close_document(document):
		if document.check_for_save():
				save.save_document(document)
		docManager.del_file(document)
		if document == capi.currentDocument:
			docToDisplay = None
			try :
				docToDisplay = capi.documents['0']
			except ValueError:
				pass
			capi.currentDocument = docToDisplay

class open(Action):
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
		if capi.file_is_opened(fileToOpen):
			doc = capi.get_file(fileToOpen)
		else:
			doc = capi.new_file(fileToOpen)
		doc.load()
		capi.currentDocument = doc
		if lineToGo:
			capi.currentView.goto_line(lineToGo-1)

	@accelerators(Accelerator("<Control>o"))
	def run(cls, args=[]):
		if len(args)>=1:
			for fileToOpen in args:
				cls.open_a_file(fileToOpen)
		else:
			path = None
			currentDoc = capi.currentDocument
			if currentDoc:
				path = currentDoc.get_path()
				if path: path = os.path.dirname(path)
			fileToOpen = capi.ask_for_filename_to_open(title="Open a file", defaultDir=path)
			cls.open_a_file(fileToOpen)

class quit(Action):
	def run(cls, args=[]):
		closeall()
		capi.quit()
	
class closeall(Action):
	def run(cls, args=[]):
		for (doc, ) in capi.documents:
			close.close_document(doc)

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
			capi.currentViewContainer.split(args[1])
		if args[0] == cls.UNSPLIT:
			capi.currentViewContainer.unsplit()

class search(Action):
	import re
	lastDirection = None
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
			return [cls.lastDirection, cls.lastSearch]
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

	@accelerators(Accelerator("F3", (False,)),Accelerator("<Alt>F3", (True,)))
	def research(cls, changeDirection):
		if changeDirection:
			direction = not cls.lastDirection
		else:
			direction = cls.lastDirection
		if direction != None and cls.lastSearch != None:
			return capi.currentView.search(direction, cls.lastSearch)

	def run(cls, args=[]):
		direction = cls.lastDirection
		search = cls.lastSearch
		if len(args) > 0:
			direction = args[0]
			cls.lastDirection = direction
		if len(args) > 1:
			search = args[1]
			cls.lastSearch = search
		if direction != None and search != None:
			return capi.currentView.search(direction, search)

class goto(Action):
	def run(cls, args=[]):
		if len(args) and args[0]:
			try :
				line = int(args[0])
				capi.currentView.goto_line(line-1)
			except:
				pass
