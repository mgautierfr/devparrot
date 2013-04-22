import Tkinter

PREFIX = "tkController"

def bind(*events):
    def decorator(func):
        func.tkevent = events
        return func
    return decorator

class Modifiers(object):
    _shift, _lock, _ctrl, _alt, _numlock, _meta, _super, _altgr, _button1, _button2, _button3, _unknown1, _unknown2, _unknown3, _unknown4 = (2**i for i in xrange(0, 15))
    # _unknown2 seems to be activate when we are in alternate keymap (in linux/X/gnome)
    def __init__(self, event):
        state = event.state
        self.modifiers = set()
        for level in [2**i for i in xrange(15, -1, -1)]:
            if state >= level:
                self.modifiers.add(level)
                state -= level
            

    def __getattr__(self, name):
        level = getattr(self, "_"+name)
        return level in self.modifiers
            

class Controller(object):
    def __init__(self):
        self.tag = PREFIX + str(id(self))
    
    def configure(self, master):
        def bind(event, handler):
            master.bind_class(self.tag, event, handler)
        self.create(bind)

    def create(self, handle):
        for key in dir(self):
            method = getattr(self, key)
            if hasattr(method, "tkevent") and callable(method):
                for eventSequence in method.tkevent:
                    handle(eventSequence,
                           lambda event, method=method: method(event, Modifiers(event))
                          )

class ControllerMode:
    def __init__(self):
        self.subControllers = []
        self.configured = False
    
    def set_subControllers(self, *controllers):
        self.subControllers.extend(controllers)
    
    def install(self, widget):
        if not self.configured:
            self.configure()
        widgetclass = widget.winfo_class()
        # remove widget class bindings and other controllers
        tags = list(widget.bindtags())
        i = tags.index(widgetclass)
        tags[i:i+1] = [c.tag for c in self.subControllers]
        widget.bindtags(tuple(tags))
    
    def configure(self, master=None):
        if master is None:
            master = Tkinter._default_root
        assert master is not None
        for controller in self.subControllers:
            controller.configure(master)
