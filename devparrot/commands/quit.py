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
from devparrot.core.errors import UserCancel
from devparrot.core import session


@Command()
def quit():
    """quit devparrot"""
    from devparrot.core import ui
    documents_edited = [d for d in session.get_documentManager() if d.is_modified()]
    if documents_edited:
        if not ui.helper.ask_questionYesNo("Quit ?", "Some files are modified, do you really want to quit ?"):
            raise UserCancel()
    session.commands.core.quit()
