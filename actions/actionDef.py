

class Action:
	actionList = {}

	def get_callback(self, session, helper):
		def callback(accel_group, acceleratable, keyval, modifier):
			return self.run(session, helper, [])
		return callback
		
	def __init__(self, accelerator=None):
		self.accelerator = accelerator
	
	def __call__(self, function):
		self.name = function.__name__
		self.function = function
		Action.actionList[self.name] = self

		def wrapped_f(session, helper, args=[]):
			return function(session, helper, args)
		return wrapped_f

	def run(self, session, helper, args):
		return self.function(session, helper, args)
