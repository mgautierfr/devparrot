
window = None
helperManager = None

def init():
    global window
    global helperManager
    import mainWindow, workspace, helper
    from devparrot.core import session, command
    window = mainWindow.MainWindow()
    session.set_globalContainer(window.get_globalContainer())
    session.set_workspace(workspace.Workspace())
    command.binder.bind(window)
    helperManager = helper.HelperManager(window)
