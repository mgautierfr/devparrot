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
import constraints

import os
import core.capi as capi

import core.config

class save(Action):
	@staticmethod
	def get_default():
		if capi.currentDocument is None:
			raise constraints.noDefault()
		if capi.currentDocument.has_a_path():
			return capi.currentDocument.get_path()
		raise constraints.noDefault()

	fileName = constraints.File(mode='save', default=lambda:save.get_default())

	def pre_check(cls, cmdText):
		return capi.currentDocument is not None

	def run(cls, cmdText, fileName, *args):
		return save.save_document(capi.currentDocument,fileName)

	@staticmethod
	def save_document(document, fileToSave):
		if document.has_a_path() and document.get_path() == fileToSave:
				return document.write()

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
	document = constraints.OpenDocument()
	def run(cls, cmdText, document, *args):
		capi.currentDocument = document
		return True
		
		
class close(Action):
	documents = constraints.OpenDocument(multiple=True, default=lambda:capi.currentDocument)
	def pre_check(cls, cmdText):
		return capi.currentDocument is not None

	def run(cls, cmdText, documents, *args):
		for document in documents:
			close.close_document(document)
		return True

	@staticmethod
	def close_document(document):
		if document.check_for_save():
			save.save_document(document)
		if document.documentView.is_displayed():
			parentContainer = document.documentView.get_parentContainer()
			parentContainer.detach_child(document.documentView)
			if parentContainer.get_nbChildren() == 0:
				capi.unsplit(parentContainer)
		capi.del_file(document)

class open(Action):
	files = constraints.File(mode='open', multiple=True)
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
			doc.goto_index("%s.0"%lineToGo-1)
		return True

	def run(cls, cmdText, files, *args):
		ret = True
		for fileToOpen in files:
			ret = ret and cls.open_a_file(fileToOpen)
		return ret

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
			return ("search", match.groups())
		match = re.match(r"^\?(.*)$", line)
		if match:
			return ("bsearch", match.groups())
		return None

	core.controler.add_expender(lambda line : search.regChecker(line))
	core.controler.add_alias("bsearch", "search", 1)
	searchText = constraints.Default(optional=True)
	def run(cls, cmdText, searchText):
		print searchText
		backward = (cmdText == "bsearch")
		if searchText is None:
			searchText = cls.lastSearch
		else:
			cls.lastSearch = searchText
		if searchText:
			return capi.currentDocument.search(backward, searchText)

class goto(Action):
	@staticmethod
	def regChecker(line):
		import re
		match = re.match(r"^g(?P<line>[0-9]+)(?P<dot>\.)?(?(dot)(?P<char>[0-9]+))$", line)
		if match:
			return ("goto",["%s.%s"%(match.group('line'),match.group('char') or '0')])
		return None
	core.controler.add_expender(lambda line : goto.regChecker(line))
	def run(cls, cmdText, *indexes):
		index = " ".join(indexes)
		capi.currentDocument.goto_index(index)

