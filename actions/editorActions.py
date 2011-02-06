
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

