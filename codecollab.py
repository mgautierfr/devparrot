#!/usr/bin/python


import gtk
import sys


from session import Session
from mainWindow import MainWindow
from controler import Controler

class CodeCollab(object):
	def __init__(self):
		self.mainWindow = MainWindow()
		self.session = Session(self.mainWindow.workspaceContainer)
		self.controler = Controler(self.session, self.mainWindow)

if __name__ == "__main__":
	app = CodeCollab()
	gtk.main()
