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
import ttk

import core.config

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

def quit(event):
	from actions.controlerActions import quit
	quit.run()


def init():
	from views.documentListView import DocumentListView
	global window
	global entry
	global documentListView
	global workspaceContainer
	global accelGroup
	window = ttk.Tkinter.Tk()
	geom = window.wm_geometry()
	x = geom.split('+')[1]
	y = geom.split('+')[2]
	window.wm_geometry("%dx%d+%s+%s"%(core.config.getint('window','width'),core.config.getint('window','height'),x,y))
	icon_path = os.path.dirname(os.path.realpath(__file__))
	icon_path = os.path.join(icon_path,"../resources/icon.png")
#	window.wm_iconwindow(icon_path)
	window.wm_title("DevParrot")
	
	vbox = ttk.Tkinter.Frame(window)
	vbox.pack(expand=True,fill=ttk.Tkinter.BOTH)
	entry = ttk.Entry(vbox)
	entry.pack(side=ttk.Tkinter.TOP,fill=ttk.Tkinter.X)
	hpaned = ttk.Tkinter.PanedWindow(vbox,orient=ttk.Tkinter.HORIZONTAL)
	hpaned.pack(expand=True,fill=ttk.Tkinter.BOTH)
	documentListView = DocumentListView(hpaned)
	hpaned.add(documentListView)
	#scrolledWin = gtk.ScrolledWindow()
	#scrolledWin.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
	#hpaned.add(scrolledWin)
	#scrolledWin.add(documentListView)
	workspaceContainer = ttk.Tkinter.Frame(hpaned)
	hpaned.add(workspaceContainer)
	#hpaned.props.position = 200

	#accelGroup = gtk.AccelGroup()
	#window.add_accel_group(accelGroup)
	
	window.bind("<Control-Return>", lambda event: entry.focus())

#	window.show_all()

