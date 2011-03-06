#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
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
#    Copyright 2011 Matthieu Gautier

from actionDef import Action
import controler
import gtk

@Action()
def cut(args=[]):
	controler.currentSession.get_currentDocument().cut_clipboard(gtk.clipboard_get(), True);

@Action()
def copy(args=[]):
	controler.currentSession.get_currentDocument().copy_clipboard(gtk.clipboard_get());

@Action()
def paste(args=[]):
	controler.currentSession.get_currentDocument().paste_clipboard(gtk.clipboard_get(), None, True);

