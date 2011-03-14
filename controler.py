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

from textFile import TextFile

from actions import ActionList

import os,sys

import mainWindow

currentSession = None

def init():
	mainWindow.entry.connect('activate', on_entry_activate)
	connect_actions()
	pass

def set_session(session):
	global currentSession
	currentSession = session

def connect_actions():
	for action in ActionList:
		if "accelerators" in action.__dict__:
			for accel in action.accelerators:
				mainWindow.accelGroup.connect_group(accel[0], accel[1],
			                                    accel_flags=0,
			                                    callback=action.callback)

def on_entry_activate(sourceWidget, userData=None):
	text = sourceWidget.get_text()
	for action in ActionList:
		args = action.regChecker(text)
		if args != None :
			action.run(args)
			break
	sourceWidget.set_text('')
	currentSession.get_workspace().get_currentView().grab_focus()

