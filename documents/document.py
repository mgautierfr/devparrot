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

from views.documentView import DocumentView

class Document():
	def __init__(self):
		self.models = {}
		for model_type in self.__class__.__models__:
			self.models[model_type] = self.__class__.__models__[model_type](self)
		self.views = []
		self.documentView = DocumentView(self)
		self.currentView = None
		pass
	
	def __getattr__(self, name):
		if name in ["title", "longTitle"]:
			print "WARNING : Sub class of document must have a attribute named %s"%name
		raise AttributeError
		
	def add_view(self, model_type, view):
		if self.currentView != None:
			print "NYI : Only one view per document for now"
			return
		self.views.append(view)
		view.set_model(self.models[model_type])
		self.documentView.set_view(view)
		self.currentView = view
		
	def remove_view(self, model_type, view):
		if self.models[model_type] in self.views.keys():
			self.views[self.models[model_type]].remove(view)
		self.documentView.remove_view(view)
		view.set_model(None)
		if self.currentView == view : self.currentView = None
		
	def get_currentView(self):
		return self.currentView