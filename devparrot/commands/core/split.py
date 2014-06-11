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
from devparrot.core.constraints import Boolean

@Command(
_section='core',
vertical = Boolean(default= lambda : False)
)
def split(vertical):
    """split the view it two separate panes"""
    from devparrot.core import session
    from devparrot.core.ui import viewContainer
    viewContainer.split(session.get_currentContainer().get_documentView(), vertical, True)

@Command(_section='core')
def unsplit():
    """unsplit (merge) two separate panes"""
    from devparrot.core import session
    from devparrot.core.ui import viewContainer
    container = session.get_currentContainer()
    viewContainer.unsplit(container)
