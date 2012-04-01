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

class Variable():
	def __init__(self, value=None):
		self._value = value
		self._callbacks = {}
		self._nextId = 0
	
	def set(self, value):
		self._value = value
		self.notify()
		
	def notify(self):
		map(lambda cb : cb(self), self._callbacks.itervalues())
	
	def get(self):
		return self._value
	
	def register(self, callback):
		self._callbacks[self._nextId] = callback
		self._nextId += 1
		return self._nextId-1
	
	def __str__(self):
		return str(self.get())
	
	def __repr__(self):
		return "< Variatic : [%s] >"%str(self)

class ProxyVar(Variable):
	def __init__(self, getcall):
		Variable.__init__(self, getcall)
	
	def set(self, value):
		pass
	
	def get(self):
		return self._value()

