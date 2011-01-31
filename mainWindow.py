

import gtk


class MainWindow(object):
	class Helper:
		def __init__(self, window):
			self.window = window

		def ask_questionYesNo(self, title, message):
			dialog = gtk.MessageDialog(self.window,
			                           gtk.DIALOG_MODAL | gtk.DESTROY_WITH_PARENT,
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

		def ask_filenameOpen(self, title):
			chooser = gtk.FileChooserDialog(title,
			                                self.window,
			                                gtk.FILE_CHOOSER_ACTION_OPEN,
			                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			                                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))

			response = None
			if chooser.run() == gtk.RESPONSE_OK:
				response = chooser.get_filename()
			chooser.destroy()
			return response

	def __init__(self):
		self.window = gtk.Window()
		self.window.connect('destroy', gtk.main_quit)
		vbox = gtk.VBox()
		self.window.add(vbox)
		self.entry = gtk.Entry()
		vbox.add(self.entry)
		vbox.child_set_property(self.entry, "expand", False)
		self.workspaceContainer = gtk.VBox()
		vbox.add(self.workspaceContainer)

		self.accelGroup = gtk.AccelGroup()
		self.window.add_accel_group(self.accelGroup)
	
		self.entry.add_accelerator('grab-focus', self.accelGroup, *gtk.accelerator_parse("<Control>Return") , accel_flags = 0)
		self.accelGroup.connect_group(*gtk.accelerator_parse("<Control>s"), accel_flags=0, callback = self.on_accel)
		self.accelGroup.connect_group(*gtk.accelerator_parse("<Control>o"), accel_flags=0, callback = self.on_accel)
		self.accelGroup.connect_group(*gtk.accelerator_parse("<Control>n"), accel_flags=0, callback = self.on_accel)
		self.accelGroup.connect_group(*gtk.accelerator_parse("<Control>q"), accel_flags=0, callback = self.on_accel)

		self.window.show_all()
		self.helper = MainWindow.Helper(self.window)
		
		pass

	def on_accel(self,accel_group, acceleratable, keyval, modifier):
		if (keyval, modifier) == gtk.accelerator_parse("<Control>s"):
			self.entry.set_text("save")
			self.entry.activate()
			return True
		if (keyval, modifier) == gtk.accelerator_parse("<Control>o"):
			self.entry.set_text("open")
			self.entry.activate()
			return True
		if (keyval, modifier) == gtk.accelerator_parse("<Control>n"):
			self.entry.set_text("new")
			self.entry.activate()
			return True
		if (keyval, modifier) == gtk.accelerator_parse("<Control>q"):
			self.entry.set_text("quit")
			self.entry.activate()
			return True
		return False

	def get_helper(self):
		return self.helper
