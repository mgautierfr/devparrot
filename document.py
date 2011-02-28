#    This file is part of CodeCollab.
#
#    Author: Matthieu Gautier <matthieu.gautier@mgautier.fr>
#
#    CodeCollab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CodeCollab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CodeCollab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011 Matthieu Gautier

class Document():
	def __init__(self):
		self.models = {}
		pass
		
	def get_model(self,repr_type):
		if repr_type not in self.__class__.__models__:
			raise KeyError()
		if repr_type not in self.models:
			self.models[repr_type] = self.__class__.__models__[repr_type](self)
		return self.models[repr_type] 