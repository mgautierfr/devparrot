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

from devparrot.core.command.baseCommand import Command
from devparrot.core.command import constraints, capi

class goto(Command):
	@staticmethod
	def regChecker(line):
		import pyparsing
		if not line:
			return None

		if line[0] != "g":
			return None
		
		line = line[1:]
		
		try:
			goto.index.grammar.parseString(line)
		except pyparsing.ParseException:
			return None
		
		return ("goto", line)

	Command.add_expender(lambda line : goto.regChecker(line))
	index = constraints.Index()
	def run(cls, index):
		try:
			capi.currentDocument.goto_index(index)
		except Exception:
			return False
		return True

