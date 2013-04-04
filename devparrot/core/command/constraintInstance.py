

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

    def get_help(self):
        attr_text = ",".join( (attribute for attribute in ("optional", "askUser", "default", "multiple", "isVararg") if getattr(self.constraint, attribute) ) )
        text = " - %(name)s: (%(attr)s)\n      [%(constraintHelp)s]\n     %(userHelp)s"%{'name':self.name, 'attr':attr_text, 'constraintHelp':self.constraint.__class__.__doc__ or "", 'userHelp':self.constraint.get_help()}
        return text
                
