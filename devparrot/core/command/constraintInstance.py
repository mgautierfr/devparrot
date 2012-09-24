from tokenParser import MissingToken, InvalidToken

class ConstraintInstance(object):
    def __init__(self, constraint, name):
        self.constraint = constraint
        self.name = name

    def __getattr__(self, name):
        attr = getattr(self.constraint, name)
        if callable(attr):
            def f(*args, **kwords):
                try:
                    return attr(*args, **kwords)
                except MissingToken:
                    raise MissingToken(self)
                except InvalidToken:
                    raise InvalidToken(self)
            return f
        return attr

    def __str__(self):
        return '"%s" (of type %s)' % (self.name, self.constraint.__class__.__name__)
