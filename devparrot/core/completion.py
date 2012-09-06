import Tkinter

def escape_token(value):
    if set("'\"\\ ") | set(value):
        for specialChar in "'\"\\ ":
            value = value.replace(specialChar, '\\'+specialChar)
    return value

class Completion(object):
    def __init__(self, value, final):
        self.value = value
        self.final = final

    def __str__(self):
        template = "%s " if self.final else "%s"
        return template%escape_token(self.value.encode("utf8"))


def getcommonstart(seq):
    if not seq:return ""
    s1, s2 = min(seq), max(seq)
    l = min(len(s1), len(s2))
    if l == 0 :
        return ""
    for i in xrange(l) :
        if s1[i] != s2[i] :
            return s1[:i]
    return s1[:l]



class CompletionSystem(object):
    def __init__(self, textWidget):
        self.textWidget = textWidget
        self._create_listboxWidget()
        self.update_completion("1.0", [])

    def _create_listboxWidget(self):
        self.toplevel = Tkinter.Toplevel()
        self._hide()
        self.toplevel.wm_overrideredirect(True)
        self.toplevel.bind('<FocusOut>', self.on_lost_focus)
        

        self.listbox = Tkinter.Listbox(self.toplevel)
        self.listbox.pack(expand=True, fill=Tkinter.BOTH)
        self.toplevel.pack_propagate(True)
        self.listbox.bind('<Key>', self.on_event)

    def _show(self):
        self.displayed = True
        self.set_position()
        self.toplevel.deiconify()

    def _hide(self):
        self.displayed = False
        self.toplevel.withdraw()

    def set_position(self):
        x, y, width, height = self.textWidget.bbox(self.startIndex)
        xpos = self.textWidget.winfo_rootx() + x
        ypos = self.textWidget.winfo_rooty() + y + height
        self.toplevel.wm_geometry("+%d+%d"% (xpos, ypos))
        self.toplevel.wm_geometry("")
        #self.toplevel.minsize(width=self.textWidget.winfo_width(), height=0)

    def on_lost_focus(self, event):
        self._hide()

    def start_completion(self):
        self._show()
        self.listbox.focus()
        self.listbox.select_set(0)

    def stop_completion(self):
        self._hide()
        self.textWidget.focus()

    def complete(self, toInsert):
        startIndex = self.startIndex
        toInsert = str(toInsert)
        self.textWidget.delete(startIndex, 'insert')
        self.textWidget.insert(startIndex, toInsert)
        self.textWidget.mark_set("insert", startIndex + " + %dc"%len(toInsert))

    def get_selected(self):
        return self.completions[int(self.listbox.curselection()[0])]

    def get_common(self):
        return self.commonString
        
    def on_event(self, event):
        from pyparsing import printables
        if event.keysym == 'Escape':
            self.stop_completion()
            return
        if event.keysym == 'Return' or (event.keysym == 'Tab' and len(self.completions) == 1):
            selected = self.get_selected()
            self.complete(selected)
            if selected.final:
                self.stop_completion()
            return
        if event.keysym == 'Tab':
            self.complete(self.get_common() or self.get_selected())
            return
        if event.keysym == 'BackSpace':
            self.textWidget.delete('insert - 1c')
            return
        char = event.char.decode('utf8')
        if char and char in printables:
            self.textWidget.insert('insert', event.char)

    def update_completion(self, startIndex, completions):
        self.startIndex = startIndex
        self.completions = completions
        self.commonString = getcommonstart([str(c) for c in completions])
        self.listbox.delete('0', 'end')
        size = 0
        for v in self.completions:
            size = max(size, len(v.value))
            self.listbox.insert('end', v.value)
        self.set_position()
        self.listbox.configure(width=size)
        self.listbox.select_set(0)
