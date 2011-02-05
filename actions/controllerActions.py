
from actionDef import Action

import gtk
import os

@Action(accelerator=gtk.accelerator_parse("<Control>s"))
def save(session, helper, args=[]):
	fileToSave = None
	currentDocument = session.get_currentDocument()
	if not currentDocument:
		return False
	if len(args)>=1:
		fileToSave = os.path.abspath(args[0])

	if currentDocument.get_path() and not fileToSave:
		currentDocument.write()
		return True

	if not currentDocument.get_path() and not fileToSave:
		fileToSave = helper.ask_filenameSave("Save")
	if not fileToSave:
		return False

	newDocument = session.get_documentManager().get_file(fileToSave, False)
	if newDocument:
		currentDocument.writeTo(fileToSave)
		newDocument.load()
		session.get_workspace().set_currentDocument(newDocument)
		session.get_documentManager().del_file(currentDocument)
	else:
		currentDocument.set_path(fileToSave)
		currentDocument.write()

	return True
#	currentDocument = session.get_documentManager().get_file(fileToSave)
#	session.get_workspace().set_currentDocument(currentDocument)

@Action(accelerator=gtk.accelerator_parse("<Control>n"))
def new(session, helper, args=[]):
	f = session.get_documentManager().new_file()
	session.get_workspace().set_currentDocument(f)

@Action()
def debug(session, helper, args=[]):
	print session.get_documentManager()

@Action(accelerator=gtk.accelerator_parse("<Control>o"))
def open(session, helper, args=[]):
	fileToOpen = None
	if len(args)>=1:
		fileToOpen = os.path.abspath(args[0])
	if not fileToOpen:
		fileToOpen = helper.ask_filenameOpen("Open a file")
	if not fileToOpen : return

	f = session.get_documentManager().get_file(fileToOpen)
	f.load()
	session.get_workspace().set_currentDocument(f)

@Action()
def quit(session, helper, args=[]):
	import gtk
	gtk.main_quit()
