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


import sys

import core.config
import core.mainWindow
from core.session import Session
import core.controler

class DevParrot(object):
	def __init__(self):
		core.mainWindow.init()
		core.controler.init()
		self.session = Session()
		if len(sys.argv) > 1:
			core.controler.run_command("open %s"%" ".join(sys.argv[1:]))

if __name__ == "__main__":
	app = DevParrot()
	core.mainWindow.window.mainloop()
