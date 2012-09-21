
window = None


def Helper():
    from helper import Helper
    return Helper(window)

def init():
    global window
    import mainWindow
    import workspace
    from devparrot.core import session, command
    window = mainWindow.MainWindow()
    session.set_globalContainer(window.get_globalContainer())
    session.set_workspace(workspace.Workspace())
    command.binder.bind(window)
    
def add_helper(widget, pos):
    if pos == 'left':
        window.hpaned.insert(0, widget)
    if pos == 'right':
        window.hpaned.insert('end', widget)
    if pos == 'top':
        window.vpaned.insert(0, widget)
    if pos == 'bottom':
        window.vpaned.insert('end', widget)
