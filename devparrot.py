#!/usr/bin/python

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


import gtk
import sys


from session import Session

import mainWindow
import controler

class DevParrot(object):
	def __init__(self):
		mainWindow.init()
		controler.init()
		self.session = Session()
		if len(sys.argv) > 1:
			command = controler.get_command('open')
			command.run(sys.argv[1:])

if __name__ == "__main__":
	app = DevParrot()
	gtk.main()
