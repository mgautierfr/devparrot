#!/usr/bin/env python

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

import os.path
from devparrot.core import config, ui, session, commandLauncher, command, modules

class DevParrot(object):
    def __init__(self):
        ui.mainWindow.init()
        commandLauncher.init()
        currentPath = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        devparrotPath = os.path.join(os.path.dirname(currentPath), "devparrot")
        command.init(devparrotPath)
        modules.init(devparrotPath)
        self.session = session.Session()
#		ui.mainWindow.window.mainloop()
