

class ConstraintInstance(object):
    def __init__(self, constraint, name):
        self.constraint = constraint
        self.name = name

    def __getattr__(self, name):
        attr = getattr(self.constraint, name)
        if callable(attr):
            def f(*args, **kwords):
                return attr(*args, **kwords)
            return f
        return attr

    def __str__(self):
        return '"%s" (of type %s)' % (self.name, self.constraint.__class__.__name__)
