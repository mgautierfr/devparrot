#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
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
#    Copyright 2011-2013 Matthieu Gautier

from index import Start

class Mark(object):
	is_index = True
	_reduced = {"i":"insert", "c":"current"}
	def __init__(self, markName):
		self.markName = self._reduced.get(markName, markName)

	def resolve(self, model):
		if self.markName == "start":
			return Start
		return model.index(self.markName)

	def __eq__(self, other):
		return (self.__class__, self.markName) == (other.__class__, other.markName)

	def __str__(self):
		return "<MARK %s>"%self.markName


