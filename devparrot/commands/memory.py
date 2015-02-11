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


from devparrot.core.command import Command
from devparrot.core.constraints import Stream

@Command(
content = Stream()
)
def memory(name, content=set()):
    """
    represent a memory space where you can put data or take data from.
    the memory can be used as stream sink or stream source. (but not both)
    if name is "CLIPBOARD" then system clipboard is used
    if name is "PRIMARY" then system primary selection (middle click) is used
    """

    if name in ('CLIPBOARD',):
        from devparrot.core import session
        window = session.window
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
