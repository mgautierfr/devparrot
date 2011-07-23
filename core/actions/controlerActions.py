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
import core.capi as capi

import core.config

class save(Action):

	@accelerators(Accelerator(core.config.get('binding','save_command')))
	def run(cls, args=[]):
		if len(args)>=1:
			return save.save_document(capi.currentDocument,os.path.abspath(args[0]))
		else:
			return save.save_document(capi.currentDocument, None)

	@staticmethod			
	def save_document(document, fileToSave=None):
		if not document: return False
		if document.has_a_path() and not fileToSave:
			return document.write()

		if not document.has_a_path() and not fileToSave:
			fileToSave = capi.ask_for_filename_to_save(title="Save")

		if not fileToSave:
			return False

		if capi.file_is_opened(fileToSave):
			#The document is already opened.
			#do nothing (should warn)
			return False
		
		from documents.fileDocSource import FileDocSource
		document.set_path(FileDocSource(fileToSave))
		return document.write()


class new(Action):
	@accelerators(Accelerator(core.config.get('binding','new_command')))
	def run(cls, args=[]):
		from documents.document import Document
		from documents.newDocSource import NewDocSource
		document = Document(NewDocSource())
		capi.add_file(document)
		capi.currentDocument = document
		return True

class switch(Action):
	def run(cls, args=[]):
		if len(args)==0:
			return False
		capi.currentDocument = capi.get_nth_file(args[0])
		return True
		
		
class close(Action):
	def run(cls, args=[]):
		if len(args)==0 or not args[0]:
			document = capi.currentDocument
		else:
			path = args[0]
			document = capi.documents[path]
		return close.close_document(document)

	@staticmethod
	def close_document(document):
		if document.check_for_save():
			save.save_document(document)
		if document.documentView.is_displayed():
			document.documentView.get_parentContainer().undisplay(document.documentView)
		return capi.del_file(document)

class open(Action):
	def open_a_file(cls, fileToOpen):
		if not fileToOpen: return False
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
			from documents.document import Document
			from documents.fileDocSource import FileDocSource
			doc = Document(FileDocSource(fileToOpen))
			capi.add_file(doc)
		doc.load()
		capi.currentDocument = doc
		if lineToGo:
			doc.goto_line(lineToGo-1)
		return True

	@accelerators(Accelerator(core.config.get('binding','open_command')))
	def run(cls, args=[]):
		if len(args)>=1:
			ret = True
			for fileToOpen in args:
				ret = ret and cls.open_a_file(fileToOpen)
			return ret
		else:
			path = None
			currentDoc = capi.currentDocument
			if currentDoc:
				path = currentDoc.get_path()
				if path: path = os.path.dirname(path)
			fileToOpen = capi.ask_for_filename_to_open(title="Open a file", defaultDir=path)
			return cls.open_a_file(fileToOpen)

class quit(Action):
	def run(cls, args=[]):
		closeall()
		return capi.quit()
	
class closeall(Action):
	def run(cls, args=[]):
		ret = True
		while len(capi.documents):
			ret = ret and close.close_document(capi.get_nth_file(0))
		return ret

class split(Action):
	SPLIT = 0
	UNSPLIT = 1

	def regChecker(cls, line):
		if line.startswith("split"):
			args = line.split()
			if len(args) != 2:
				return None
			return [cls.SPLIT, 0, args[1] ]
		if line.startswith("vsplit"):
			args = line.split()
			if len(args) != 2:
				return None
			return [cls.SPLIT, 1, args[1] ]
		if line.startswith("unsplit"):
			return [cls.UNSPLIT]
		return None

	def run(cls, args=[]):
		if args[0] == cls.SPLIT:
			doc = capi.get_nth_file(args[2])
			if doc.documentView.is_displayed():
				return doc.documentView.grab_focus()
			else:
				return capi.currentContainer.split(args[1], doc.documentView)
		if args[0] == cls.UNSPLIT:
			if capi.currentContainer.get_parentContainer():
				return capi.currentContainer.get_parentContainer().unsplit(toKeep=capi.currentContainer)
		return False

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

	@accelerators(Accelerator(core.config.get('binding','forward_research'), (False,)),Accelerator(core.config.get('binding','backward_research'), (True,)))
	def research(cls, changeDirection):
		if changeDirection:
			direction = not cls.lastDirection
		else:
			direction = cls.lastDirection
		if direction != None and cls.lastSearch != None:
			return capi.currentDocument.search(direction, cls.lastSearch)

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
			return capi.currentDocument.search(direction, search)

class goto(Action):
	def regChecker(cls, line):
		import re
		if line.startswith("goto"):
			return line.split(' ')[1:]
		match = re.match(r"^g(?P<delta>[+-]?)(?P<line>[0-9]*)$", line)
		if match:
			return [match.group('line'),match.group('delta')]
		return None
	def run(cls, args=[]):
		if len(args) and args[0]:
			try :
				delta = args[1]
				line = int(args[0])
				if not delta:
					line -= 1
				return capi.currentDocument.goto_line(line, delta)
			except:
				return False
