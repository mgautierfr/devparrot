
from actionDef import Action

import gtk
import os

import controler, mainWindow

@Action(accelerator=gtk.accelerator_parse("<Control>s"))
def save(args=[]):
	fileToSave = None
	currentDocument = controler.currentSession.get_currentDocument()
	if not currentDocument:
		return False
	if len(args)>=1:
		fileToSave = os.path.abspath(args[0])

	if currentDocument.get_path() and not fileToSave:
		currentDocument.write()
		return True

	if not currentDocument.get_path() and not fileToSave:
		fileToSave = mainWindow.Helper().ask_filenameSave("Save")
	if not fileToSave:
		return False

	(newDocument, newOne) = controler.currentSession.get_documentManager().get_file(fileToSave, False)
	if newDocument:
		currentDocument.writeTo(fileToSave)
		newDocument.load()
		controler.currentSession.get_workspace().set_currentDocument(newDocument)
		controler.currentSession.get_documentManager().del_file(currentDocument)
	else:
		currentDocument.set_path(fileToSave)
		currentDocument.write()

	return True

@Action(accelerator=gtk.accelerator_parse("<Control>n"))
def new(args=[]):
	f = controler.currentSession.get_documentManager().new_file()
	controler.currentSession.get_workspace().set_currentDocument(f)

@Action()
def switch(args=[]):
	if len(args)==0:
		return False
	path = args[0]
	docManager = controler.currentSession.get_documentManager()
	document = docManager.get_value(docManager.get_iter(path), 0)
	controler.currentSession.get_workspace().set_currentDocument(document)

@Action()
def close(args=[]):
	docManager = controler.currentSession.get_documentManager()
	if len(args)==0 or not args[0]:
		document = controler.currentSession.get_currentDocument()
	else:
		path = args[0]
		document = docManager.get_value(docManager.get_iter(path), 0)
	docManager.del_file(document)
	if document == controler.currentSession.get_workspace().get_currentDocument():
		docToDisplay = None
		try :
			docToDisplay = docManager.get_value(docManager.get_iter("0"), 0)
		except ValueError:
			pass
		controler.currentSession.get_workspace().set_currentDocument(docToDisplay)


@Action()
def debug(args=[]):
	print controler.currentSession.get_documentManager()

@Action(accelerator=gtk.accelerator_parse("<Control>o"))
def open(args=[]):
	fileToOpen = None
	if len(args)>=1 and args[0]:
		fileToOpen = os.path.abspath(args[0])
	if not fileToOpen:
		path = None
		currentDoc = controler.currentSession.get_workspace().get_currentDocument()
		if currentDoc:
			path = currentDoc.get_path()
			if path:
				path = os.path.dirname(path)
		fileToOpen = mainWindow.Helper().ask_filenameOpen("Open a file", path)
	if not fileToOpen : return

	(doc, newOne) = controler.currentSession.get_documentManager().get_file(fileToOpen)
	if newOne:
		doc.load()
	controler.currentSession.get_workspace().set_currentDocument(doc)

@Action()
def quit(args=[]):
	import gtk
	gtk.main_quit()

@Action()
def split(args=[]):
	controler.currentSession.get_workspace().get_currentViewContainer().split(0)

@Action()
def vsplit(args=[]):
	controler.currentSession.get_workspace().get_currentViewContainer().split(1)

@Action()
def unsplit(args=[]):
	controler.currentSession.get_workspace().get_currentViewContainer().unsplit()