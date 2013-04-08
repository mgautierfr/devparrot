

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
