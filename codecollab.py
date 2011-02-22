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
		if len(sys.argv) > 1:
			command = controler.get_command('open')
			command.run(sys.argv[1:])

if __name__ == "__main__":
	app = CodeCollab()
	gtk.main()
