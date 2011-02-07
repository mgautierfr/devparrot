
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
def debug(args=[]):
	print controler.currentSession.get_documentManager()

@Action(accelerator=gtk.accelerator_parse("<Control>o"))
def open(args=[]):
	fileToOpen = None
	if len(args)>=1:
		fileToOpen = os.path.abspath(args[0])
	if not fileToOpen:
		fileToOpen = mainWindow.Helper().ask_filenameOpen("Open a file")
	if not fileToOpen : return

	(doc, newOne) = controler.currentSession.get_documentManager().get_file(fileToOpen)
	if newOne:
		doc.load()
	controler.currentSession.get_workspace().set_currentDocument(doc)

@Action()
def quit(args=[]):
	import gtk
	gtk.main_quit()
