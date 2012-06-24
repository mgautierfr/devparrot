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

import os
import core.capi as capi

import core.config

class save(Action):
	def run(cls, cmdText, *args):
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

	def run(cls, cmdText, *args):
		from documents.document import Document
		from documents.newDocSource import NewDocSource
		document = Document(NewDocSource())
		capi.add_file(document)
		capi.currentDocument = document
		return True

class switch(Action):
	def run(cls, cmdText, *args):
		if len(args)==0:
			return False
		capi.currentDocument = capi.get_nth_file(int(args[0]))
		return True
		
		
class close(Action):
	def run(cls, cmdText, *args):
		if len(args)==0 or not args[0]:
			document = capi.currentDocument
		else:
			index = args[0]
			document = capi.documents[index]
		return close.close_document(document)

	@staticmethod
	def close_document(document):
		if document.check_for_save():
			save.save_document(document)
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			parentContainer.detach_child(document.documentView)
			if parentContainer.get_nbChildren() == 0:
				capi.unsplit(parentContainer)
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

	def run(cls, cmdText, *args):
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
	def run(cls, cmdText, *args):
		closeall()
		return capi.quit()
	
class closeall(Action):
	def run(cls, cmdText, *args):
		ret = True
		while len(capi.documents):
			ret = ret and close.close_document(capi.get_nth_file(0))
		return ret

class split(Action):
	core.controler.add_alias("vsplit", "split", 1)
	core.controler.add_alias("unsplit", "split", 1)
	def run(cls, cmdText, *args):
		if cmdText in ["split", "vsplit"]:
			vertical = 1 if cmdText=="vsplit" else 0
			return capi.split(vertical)
		if cmdText == "unsplit":
			return capi.unsplit()
		return False

class search(Action):
	lastSearch = None

	@staticmethod
	def regChecker(line):
		import re
		match = re.match(r"^/(.*)$", line)
		if match:
			ret = ["search"]
			ret.extend(match.groups())
			return ret
		match = re.match(r"^\?(.*)$", line)
		if match:
			ret = ["bsearch"]
			ret.extend(match.groups())
			return  ret
		return None

	core.controler.add_expender(lambda line : search.regChecker(line))
	core.controler.add_alias("bsearch", "search", 1)
	def run(cls, cmdText, *args):
		backward = (cmdText == "bsearch")
		search = cls.lastSearch
		try:
			search = args[0]
			cls.lastSearch = search
		except : pass
		if search != None:
			return capi.currentDocument.search(backward, search)

class goto(Action):
	@staticmethod
	def regChecker(line):
		import re
		match = re.match(r"^g(?P<line>[0-9]+)(?P<dot>\.)?(?(dot)(?P<char>[0-9]+))$", line)
		if match:
			return ["goto","%s.%s"%(match.group('line'),match.group('char') or '0')]
		return None
	core.controler.add_expender(lambda line : goto.regChecker(line))
	def run(cls, cmdText, *indexes):
		index = " ".join(indexes)
		capi.currentDocument.goto_index(index)

