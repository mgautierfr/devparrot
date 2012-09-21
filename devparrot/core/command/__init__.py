import bind
import os

import baseCommand


binder = bind.Binder()

def load():
    path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    path = os.path.join(os.path.dirname(path), "..")
    path = os.path.join(path, 'actions')
    moduleList = os.listdir(path)
    for module in moduleList:
        m = load_module(path, module)
    pass

def load_module(path, name):
    import imp
    if name.endswith('.pyc'):
        return
    if name.endswith('.py'):
        name = name[:-3]

    try:
        fp, pathname, description = imp.find_module(name, [path])
    except ImportError, m:
        print m
        return

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

