import re

TkEventMatcher = re.compile(r"<.*>")

class BindLauncher(object):
    def __init__(self, command):
        self.command = command

    def __call__(self, event):
        from devparrot.core import session, ui
        commands = text.split('\n')
        for cmd in commands[:-1]:
            ret = session.commandLauncher.run_command(cmd)
            if not ret:
                return "break"
        ui.window.entry.insert("1.0", commands[-1])
        if commands[-1]:
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
