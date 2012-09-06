import Tkinter

PREFIX = "tkController"

def bind(*events):
    def decorator(func):
        func.tkevent = events
        return func
    return decorator

class Modifiers(object):
    _button3 = 1024
    _button2 = 512
    _button1 = 256
    _altgr   = 128
    _super   = 64
    _meta    = 32
    _numlock = 16
    _alt     = 8
    _ctrl    = 4
    _lock    = 2
    _shift   = 1
    def __init__(self, event):
        self.state = event.state
        self.modifiers = set()
        for level in [2**i for i in xrange(10, -1, -1)]:
            if self.state >= level:
                self.modifiers.add(level)
                self.state -= level
            

    def __getattr__(self, name):
        level = getattr(self, "_"+name)
        return level in self.modifiers
            

class Controller(object):
    def __init__(self, master=None):
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
