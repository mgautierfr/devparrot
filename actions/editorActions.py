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
import gtk

class cut(Action):
	def run(cls, args=[]):
		capi.currentDocument.cut_clipboard(gtk.clipboard_get(), True);

class copy(Action):
	def run(cls, args=[]):
		capi.currentDocument.copy_clipboard(gtk.clipboard_get());

class paste(Action):
	def run(cls, args=[]):
		capi.currentDocument.paste_clipboard(gtk.clipboard_get(), None, True);

