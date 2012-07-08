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


class Event(object):
	def __init__(self):
		self.listeners = set()
		pass

	def __call__(self, *args, **kwords):
		for listener in self.listeners:
			listener(*args, **kwords)
	
	
	def connect(self, listener):
		self.listeners.add(listener)
	__iadd__ = connect

	
	def disconnect(self, listener):
		self.listeners.discard(listener)
	__isub__ = disconnect


class EventSource(object):
	def __init__(self):
		self.events = dict()

	def connect(self, eventName, listener):
		self.events.setdefault(eventName, Event()).connect(listener)

	def event(self, eventName):
		return self.events.get(eventName, Event())


