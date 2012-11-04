import bind
import baseCommand


binder = bind.Binder()

def load():
    from pwd import getpwuid
    import os
    from devparrot.core import session
    path = os.path.join(session.config.get('devparrotPath'), "actions")
    moduleList = os.listdir(path)
    for module in moduleList:
        load_module(path, module)

    _homedir = getpwuid(os.getuid())[5]
    path = os.path.join(_homedir,'.devparrot', 'actions')
    if os.path.exists(path):
        moduleList = os.listdir(path)
        for module in moduleList:
            load_module(path, module)

def load_module(path, name):
    import imp, os
    if name.endswith('.py'):
        name = name[:-3]
    elif not os.path.isdir(os.path.join(path,name)):
        return

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError, err:
        print err
        return

    with fp:
        return imp.load_module(name, fp, pathname, description)

