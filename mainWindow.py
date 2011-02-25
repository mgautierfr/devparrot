import gtk
import os

from documentListView import DocumentListView


class Helper:
	def __init__(self):
		global window
		self.window = window

	def ask_questionYesNo(self, title, message):
		dialog = gtk.MessageDialog(self.window,
		                           gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		                           gtk.MESSAGE_QUESTION,
		                           gtk.BUTTONS_YES_NO,
		                           message)
		dialog.set_title(title)
		response = dialog.run()
		dialog.destroy()
		return (response==gtk.RESPONSE_YES)

	def ask_filenameSave(self, title):
		chooser = gtk.FileChooserDialog(title,
		                                self.window,
		                                gtk.FILE_CHOOSER_ACTION_SAVE,
		                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                 gtk.STOCK_SAVE, gtk.RESPONSE_OK))

		response = None
		if chooser.run() == gtk.RESPONSE_OK:
			response = chooser.get_filename()
		chooser.destroy()
	
		return response

	def ask_filenameOpen(self, title, currentFolder):
		chooser = gtk.FileChooserDialog(title,
		                                self.window,
		                                gtk.FILE_CHOOSER_ACTION_OPEN,
		                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		                                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		if currentFolder:
			chooser.set_current_folder(currentFolder)
		response = None
		if chooser.run() == gtk.RESPONSE_OK:
			response = chooser.get_filename()
		chooser.destroy()
		return response

window = None
entry = None
documentListView = None
workspaceContainer = None
accelGroup = None

def quit(widget,event):
	from actions.controlerActions import quit
	quit()


def init():
	
	global window
	global entry
	global documentListView
	global workspaceContainer
	global accelGroup
	window = gtk.Window()
	window.connect('delete-event', quit)
	window.set_default_size(800,600)
	icon_path = os.path.dirname(os.path.realpath(__file__))
	icon_path = os.path.join(icon_path,"icon.png")
	window.set_icon_from_file(icon_path)
	window.set_title("CodeCollab")
	vbox = gtk.VBox()
	window.add(vbox)
	entry = gtk.Entry()
	vbox.add(entry)
	vbox.child_set_property(entry, "expand", False)
	hpaned = gtk.HPaned()
	vbox.add(hpaned)
	documentListView = DocumentListView()
	scrolledWin = gtk.ScrolledWindow()
	scrolledWin.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
	hpaned.add(scrolledWin)
	scrolledWin.add(documentListView)
	workspaceContainer = gtk.VBox()
	hpaned.add(workspaceContainer)
	hpaned.props.position = 200

	accelGroup = gtk.AccelGroup()
	window.add_accel_group(accelGroup)
	
	entry.add_accelerator('grab-focus', accelGroup, *gtk.accelerator_parse("<Control>Return") , accel_flags = 0)

	window.show_all()
	

def on_accel(accel_group, acceleratable, keyval, modifier):
	global entry
	if (keyval, modifier) == gtk.accelerator_parse("<Control>s"):
		entry.set_text("save")
		entry.activate()
		return True
	if (keyval, modifier) == gtk.accelerator_parse("<Control>o"):
		entry.set_text("open")
		entry.activate()
		return True
	if (keyval, modifier) == gtk.accelerator_parse("<Control>n"):
		entry.set_text("new")
		entry.activate()
		return True
	if (keyval, modifier) == gtk.accelerator_parse("<Control>q"):
		entry.set_text("quit")
		entry.activate()
		return True
	return False

