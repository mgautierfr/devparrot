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

from devparrot.core.command import MasterCommand, SubCommand, Command
from devparrot.core import session

def _get_section(menu, sections):
    current = menu
    for section in sections:
        try:
            current = next(v for name,v in current if name==section)
        except StopIteration:
            current = current.append((section, []))[1]
    return current    

class menu(MasterCommand):
    @SubCommand()
    def add(entry, command):
        """Add a menu entry

        If the entyr already exist, it will be updated with command."""
        sections = entry.split('.')
        menu, sections, name = sections[0], sections[1:-1], sections[-1]
        menu = session.config.get(menu)
        section = _get_section(menu, sections)
        if name in section:
            section[name].set_command(command)
        else:
            section.append((name, command))

    @SubCommand(_name='del')
    def _del(entry):
        """Remove a menu entry
        """
        sections = entry.split('.')
        menu, sections, name = sections[0], sections[1:-1], sections[-1]
        menu = session.config.get(menu)
        section = _get_section(menu, sections)
        if name in section:
            del section[name]

    @SubCommand()
    def disable(entry):
        """Disable a entry (it will be greyout)"""
        sections = entry.split('.')
        menu, sections, name = sections[0], sections[1:-1], sections[-1]
        menu = session.config.get(menu)
        section = _get_section(menu, sections)
        section.entryconfigure(name, state="disable")

    @SubCommand()
    def enable(entry):
        """Enable a entry (it will be greyout)"""
        sections = entry.split('.')
        menu, sections, name = sections[0], sections[1:-1], sections[-1]
        menu = session.config.get(menu)
        section = _get_section(menu, sections)
        section.entryconfigure(name, state="normal")

    @SubCommand()
    def update_popup_menu():
        cut = copy = paste = undo = redo = (session.get_currentDocument() is not None)

        try:
            if session.get_currentDocument().is_readonly():
                cut = paste = undo = redo = False
        
            view = session.get_currentDocument().get_currentView().view
        
            if not view.sel_isSelection():
                cut = copy = False
        
            if not view.nbModif:
                undo = False
        
            if not view.nbModif < len(view.undoredoStack):
                redo = False
        except AttributeError:
            pass
    
        session.commands.menu['enable' if cut else 'disable']('popupMenu.Cut')
        session.commands.menu['enable' if copy else 'disable']('popupMenu.Copy')
        session.commands.menu['enable' if paste else 'disable']('popupMenu.Paste')
        session.commands.menu['enable' if undo else 'disable']('popupMenu.Undo')
        session.commands.menu['enable' if redo else 'disable']('popupMenu.Redo')

        session.commands.menu['enable' if cut else 'disable']('menuBar.Edit.Cut')
        session.commands.menu['enable' if copy else 'disable']('menuBar.Edit.Copy')
        session.commands.menu['enable' if paste else 'disable']('menuBar.Edit.Paste')
        session.commands.menu['enable' if undo else 'disable']('menuBar.Edit.Undo')
        session.commands.menu['enable' if redo else 'disable']('menuBar.Edit.Redo')

session.bindings["selection"] = "menu update_popup_menu\n"
session.bindings["pathChanged"] = "menu update_popup_menu\n"
session.bindings["currentChanged"] = "menu update_popup_menu\n"
