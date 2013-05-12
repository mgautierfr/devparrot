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

# This makes sure that users don't have to set up their environment
# specially in order to run these programs from bin/.

# This helper is shared by many different actual scripts.  It is not intended to
# be packaged or installed, it is only a developer convenience.  By the time
# Devparrot is actually installed somewhere, the environment should already be set
# up properly without the help of this tool.

# (Thanks to Twisted project for this script :)

import sys, os

path = os.path.abspath(sys.argv[0])
while os.path.dirname(path) != path:
    if os.path.exists(os.path.join(path, 'devparrot', '__init__.py')):
        sys.path.insert(0, path)
        break
    path = os.path.dirname(path)
