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


import re

TkEventMatcher = re.compile(r"<.*>")

class BindLauncher(object):
    def __init__(self, command):
        commands = command.split('\n')
        self.commands = commands[:-1]
        self.leftText = commands[-1]

    def __call__(self, event):
        from devparrot.core import session, ui
        for cmd in self.commands:
            ret = session.commandLauncher.run_command_nofail(cmd)
            if not ret:
                return "break"
        ui.window.entry.delete("1.0", "end")
        ui.window.entry.insert("1.0", self.leftText)
        if self.leftText:
            ui.window.entry.focus()
            ui.window.entry.mark_set("index", "end")
        return "break"

class Binder(object):
    def __init__(self):
        """ used for later bind if ui.window is not set """
        self.tkBinds = {}

        """ used for futur unbind """
        self.binds = {}

    def __setitem__(self, accel, command):
        bindLauncher = BindLauncher(command)
        if TkEventMatcher.match(accel):
            from devparrot.core import ui
            if ui.window:
                ui.window.bind_class("Command", accel, bindLauncher)
            else:
                self.tkBinds[accel] = bindLauncher
        else:
            from devparrot.core import commandLauncher
            currentBinds = self.binds.setdefault(accel, set())
            currentBinds.add(commandLauncher.eventSystem.connect(accel, bindLauncher))

    def bind(self, window=None):
        if window is None:
            from devparrot.core import ui
            window = ui.window
        if window:
            for accel, func in self.tkBinds.items():
                window.bind_class("Command", accel, func)
            self.tkBinds = []

    def __delitem__(self, accel):
        if TkEventMatcher.match(accel):
            from devparrot.core import ui
            if ui.window:
                ui.window.unbind_class("Command", accel)
            del self.tkBinds[accel]
        else:
            from devparrot.core import commandLauncher
            for bind in self.binds.get(accel, []):
                commandLauncher.eventSystem.event(accel).unregister(bind)
