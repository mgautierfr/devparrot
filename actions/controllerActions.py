
from actionDef import Action

import gtk
import os

@Action(accelerator=gtk.accelerator_parse("<Control>s"))
def save(session, helper, args=[]):
	fileToSave = None
	currentDocument = session.get_currentDocument()
	if not currentDocument:
		return
	if len(args)>=1:
		fileToSave = os.path.abspath(args[0])

	if not currentDocument.get_path():
		if not fileToSave:
			fileToSave = helper.ask_filenameSave("Save")
	if not fileToSave:
		return
	currentDocument.set_path(fileToSave)
	currentDocument.write()
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
	session.get_workspace().set_currentDocument(f)

@Action()
def quit(session, helper, args=[]):
	import gtk
	gtk.main_quit()
