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


INFO, ERROR, INVALID = range(10, 40, 10)

import logging


class UserLogger(logging.Logger):
    def __init__(self):
        self.logger = logging.getLogger("user")
        self.logger.setLevel(INFO)

    def addHandler(self, handler):
        self.logger.addHandler(handler)

    def info(self, message, *args, **kwords):
        return self.logger.log(INFO, message, *args, **kwords)

    def error(self, message, *args, **kwords):
        return self.logger.log(ERROR, message, *args, **kwords)

    def invalid(self, message, *args, **kwords):
        return self.logger.log(INVALID, message, *args, **kwords)
