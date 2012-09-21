import re

TkEventMatcher = re.compile(r"<.*>")

class TkBindLauncher(object):
    def __init__(self, command):
        self.command = command

    def __call__(self, event):
        from devparrot.core import commandLauncher
        commandLauncher.run_command(self.command)
        return "break"

class EventBindLauncher(object):
    def __init__(self, command):
        self.command = command
    
    def __call__(self, arg):
        from devparrot.core import commandLauncher
        commandLauncher.run_command(self.command)
        return "break"

class Binder(object):
    def __init__(self):
        self.tkBinds = {}
        self.binds = {}

    def __setitem__(self, accel, command):		
        if TkEventMatcher.match(accel):
            from devparrot.core import ui
            bindLauncher = TkBindLauncher(command)
            if ui.window:
                ui.window.bind_class("Command", accel, bindLauncher)
        else:
            from devparrot.core import commandLauncher
            bindLauncher = EventBindLauncher(command)
            currentBinds = self.binds.setdefault(accel, set())
            currentBinds.add(commandLauncher.eventSystem.connect(accel, bindLauncher))
        self.tkBinds[accel] = bindLauncher

    def bind(self, window=None):
        if window is None:
            from devparrot.core import ui
            window = ui.window
        if window:
            for accel, func in self.tkBinds.items():
                if TkEventMatcher.match(accel):
                    window.bind_class("Command", accel, func)

    def __delitem__(self, accel):
        if TkEventMatcher.match(accel):
            from devparrot.core import ui
            if ui.window:
                ui.window.unbind_class("Command", accel)
        else:
            from devparrot.core import commandLauncher
            for bind in self.binds.get(accel, []):
                commandLauncher.eventSystem.event(accel).unregister(bind)
        del self.tkBinds[accel]



