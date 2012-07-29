from devparrot.core.controller import ControllerMode
from devparrot.controllers.editControllers import CarretController, AdvancedTextController, BasicTextController, MouseController


class DefaultControllerMode(ControllerMode):
	def __init__(self):
		ControllerMode.__init__(self)
		self.subControllers = [ CarretController(), AdvancedTextController(), BasicTextController(), MouseController() ]
