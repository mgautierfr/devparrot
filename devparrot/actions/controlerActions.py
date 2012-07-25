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

import os

from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, capi

class save(Command):
	@staticmethod
	def get_default():
		if capi.currentDocument is None:
			raise constraints.noDefault()
		if capi.currentDocument.has_a_path():
			return capi.currentDocument.get_path()
		raise constraints.noDefault()

	fileName = constraints.File(mode=constraints.File.SAVE, default=lambda:save.get_default())

	def pre_check(cls):
		return capi.currentDocument is not None

	def run(cls, fileName, *args):
		return save.save_document(capi.currentDocument,fileName)

	@staticmethod
	def save_document(document, fileToSave):
		if document.has_a_path() and document.get_path() == fileToSave:
				return document.write()

		if capi.file_is_opened(fileToSave):
			#The document is already opened.
			#do nothing (should warn)
			return False

		from devparrot.documents.fileDocSource import FileDocSource
		document.set_path(FileDocSource(fileToSave))
		return document.write()


class new(Command):
	def run(cls, *args):
		from devparrot.core.document import Document
		from devparrot.documents.newDocSource import NewDocSource
		document = Document(NewDocSource())
		capi.add_file(document)
		capi.currentDocument = document
		return True

class switch(Command):
	document = constraints.OpenDocument()
	def run(cls, document, *args):
		capi.currentDocument = document
		return True
		
		
class close(Command):
	documents = constraints.OpenDocument(multiple=True, default=lambda:capi.currentDocument)
	def pre_check(cls):
		return capi.currentDocument is not None

	def run(cls, documents, *args):
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

class open(Command):
	files = constraints.File(mode=(constraints.File.OPEN, constraints.File.NEW), multiple=True)
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
			from devparrot.core.document import Document
			from devparrot.documents.fileDocSource import FileDocSource
			doc = Document(FileDocSource(fileToOpen))
			capi.add_file(doc)
			doc.load()
		capi.currentDocument = doc
		if lineToGo:
			doc.goto_index("%s.0"%lineToGo-1)
		return True

	def run(cls, files, *args):
		ret = True
		for fileToOpen in files:
			ret = ret and cls.open_a_file(fileToOpen)
		return ret

class quit(Command):
	def run(cls, *args):
		closeall()
		return capi.quit()
	
class closeall(Command):
	def run(cls, *args):
		ret = True
		while len(capi.documents):
			ret = ret and close.close_document(capi.get_nth_file(0))
		return ret

class split(Command):
	Command.add_alias("vsplit", "split 1", 1)
	vertical = constraints.Boolean(default= lambda : False)
	def run(cls, vertical):
		return capi.split(vertical)

class unsplit(Command):
	def run(cls):
		return capi.unsplit()

class search(Command):
	lastSearch = None

	@staticmethod
	def regChecker(line):
		import re
		match = re.match(r"^/(.*)$", line)
		if match:
			return ("search", " ".join(match.groups()))
		match = re.match(r"^\?(.*)$", line)
		if match:
			return ("search 1 ", " ".join(match.groups()))
		return None

	Command.add_expender(lambda line : search.regChecker(line))
	Command.add_alias("bsearch", "search 1", 1)
	searchText = constraints.Default(default=lambda : search.lastSearch)
	backward = constraints.Boolean(true=("backward", "1"), false=("forward", "0"), default=lambda : False)
	def run(cls, backward, searchText):
		cls.lastSearch = searchText
		if searchText:
			return capi.currentDocument.search(backward, searchText)

class goto(Command):
	@staticmethod
	def regChecker(line):
		import pyparsing
		if not line:
			return None

		if line[0] != "g":
			return None
		
		line = line[1:]
		
		try:
			goto.index.grammar.parseString(line)
		except pyparsing.ParseException:
			return None
		
		return ("goto", line)

	Command.add_expender(lambda line : goto.regChecker(line))
	index = constraints.Index()
	def run(cls, index):
		try:
			capi.currentDocument.goto_index(index)
		except Exception:
			return False
		return True

