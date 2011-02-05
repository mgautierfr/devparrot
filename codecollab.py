#!/usr/bin/python


import gtk
import sys


from session import Session

import mainWindow
import controler

class CodeCollab(object):
	def __init__(self):
		mainWindow.init()
		controler.init()
		self.session = Session()

if __name__ == "__main__":
	app = CodeCollab()
	gtk.main()
