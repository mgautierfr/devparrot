#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
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
#    Copyright 2011-2013 Matthieu Gautier


window = None
helperManager = None

def init():
    global window
    global helperManager
    import mainWindow, workspace, helper
    from devparrot.core import session
    window = mainWindow.MainWindow()
    session.set_globalContainer(window.get_globalContainer())
    session.set_workspace(workspace.Workspace())
    session.bindings.bind(window)
    helperManager = helper.HelperManager(window)
