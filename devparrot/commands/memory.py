from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, binder
from devparrot.core import capi
from devparrot.core.utils.posrange import Index

@Command(
content = constraints.Stream()
)
def memory(name, content):
    """
    represent a memory space where you can put data or take data from.
    the memory can be used as stream sink or stream source. (but not both)
    if name is "CLIPBOARD" then system clipboard is used
    if name is "PRIMARY" then system primary selection (middle click) is used
    """

    if name in ('CLIPBOARD'):
        from devparrot.core import ui
        window = ui.window
        clear_function = window.clipboard_clear
        append_function = window.clipboard_append
        def gen_function():
            yield window.clipboard_get()
    else:
        from devparrot.core import session
        mem = session.memories.setdefault(name, [])
        def clear_function():
            mem[:] = []
        append_function = mem.append
        def gen_function():
            for m in mem:
                yield m

    insertionMode = False

    for c in content:
        if not c:
            continue
        if not insertionMode:
            insertionMode = True
            clear_function()

        append_function(c)

    if insertionMode:
        return

    return gen_function()
