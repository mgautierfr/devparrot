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

class Action:
	actionList = {}

	def callback(self, accel_group, acceleratable, keyval, modifier):
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
