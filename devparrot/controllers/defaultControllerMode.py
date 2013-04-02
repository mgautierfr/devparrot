from devparrot.core.controller import ControllerMode
from devparrot.controllers import editControllers, readOnlyControllers


class DefaultControllerMode(ControllerMode):
    def __init__(self):
        ControllerMode.__init__(self)
        self.subControllers = [ readOnlyControllers.CarretController(), editControllers.KeyboardController(), readOnlyControllers.MouseController(), editControllers.MouseController() ]


class DefaultROControllerMode(ControllerMode):
    def __init__(self):
        ControllerMode.__init__(self)
        self.subControllers = [ readOnlyControllers.CarretController(), readOnlyControllers.MouseController() ]
