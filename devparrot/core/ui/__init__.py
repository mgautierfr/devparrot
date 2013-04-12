
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
