from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, capi


class split(Command):
	Command.add_alias("vsplit", "split 1", 1)
	vertical = constraints.Boolean(default= lambda : False)
	def run(cls, vertical):
		return capi.split(vertical)

class unsplit(Command):
	def run(cls):
		return capi.unsplit()

