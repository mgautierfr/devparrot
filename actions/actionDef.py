

class Action:
	actionList = {}

	def callback(accel_group, acceleratable, keyval, modifier):
		return self.run([])
		
	def __init__(self, accelerator=None):
		self.accelerator = accelerator
	
	def __call__(self, function):
		self.name = function.__name__
		self.function = function
		Action.actionList[self.name] = self
		return function

	def run(self, args):
		return self.function(args)
