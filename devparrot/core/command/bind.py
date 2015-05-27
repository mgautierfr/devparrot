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

class BindLauncher:
    def __init__(self, command):
        commands = command.split('\n')
        self.commands = commands[:-1]
        self.leftText = commands[-1]

    def __call__(self, kwords):
        from devparrot.core import session
        for cmd in self.commands:
            ret = session.commandLauncher.run_command_nofail(cmd, kwords)
        session.window.entry.delete("1.0", "end")
        session.window.entry.insert("1.0", self.leftText)
        if self.leftText:
            session.window.entry.toClean = False
            session.window.entry.focus()
            session.window.entry.mark_set("index", "end")
        return "break"

class TkBindLauncher(BindLauncher):
    def __call__(self, event):
        return BindLauncher.__call__(self, {'event':event})

class CommandBindLauncher(BindLauncher):
    def __call__(self, *args):
        kwords = {str(i):arg for i, arg in enumerate(args)}
        return BindLauncher.__call__(self, kwords)

class Binder:
    def __init__(self):
        """ used for later bind if ui.window is not set """
        self.tkBinds = {}

    def __setitem__(self, accel, command):
        from devparrot.core import session
        if TkEventMatcher.match(accel):
            bindLauncher = TkBindLauncher(command)
            if session.window:
                session.window.bind_class("devparrot", accel, bindLauncher)
            else:
                self.tkBinds[accel] = bindLauncher
        else:
            if accel not in session.config.hook:
                session.config.hook.add_option(accel, default=[])
            getattr(session.config.hook, accel).get().append(command)

    def bind(self, window=None):
        if window is None:
            from devparrot.core import session
            window = session.window
        if window:
            for accel, func in self.tkBinds.items():
                window.bind_class("devparrot", accel, func)
            self.tkBinds = {}

    def __delitem__(self, accel):
        from devparrot.core import session
        if TkEventMatcher.match(accel):
            if session.window:
                session.window.unbind_class("devparrot", accel)
            try:
                del self.tkBinds[accel]
            except KeyError:
                pass
        else:
            getattr(session.config.bindings, accel).set([])
