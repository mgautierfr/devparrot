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


import new

from weakref import ref
import inspect

class MethodeCb(object):
    def __init__(self, mtd):
        try:
            try:
                self.inst = ref(mtd.im_self)
            except TypeError:
                self.inst = None
            self.func = mtd.im_func
            self.klass = mtd.im_class
        except AttributeError:
            self.inst = None
            self.func = mtd.im_func
            self.klass = None
    
    def __call__(self, *args, **kwargs):
        '''
        Proxy for a call to the weak referenced object. Take arbitrary params to
        pass to the callable.
        
        @raise ReferenceError: When the weak reference refers to a dead object
        '''
        if self.inst is not None:
            inst = self.inst()
            if inst is None:
                raise ReferenceError
    
            # build a new instance method with a strong reference to the instance
            mtd = new.instancemethod(self.func, inst, self.klass)
        else:
            # not a bound method, just return the func
            mtd = self.func
        # invoke the callable and return the result
        return mtd(*args, **kwargs)

    def __eq__(self, other):
        '''
        Compare the held function and instance with that held by another proxy.
        
        @param other: Another proxy object
        @type other: L{Proxy}
        @return: Whether this func/inst pair is equal to the one in the other
        proxy object or not
        @rtype: boolean
        '''
        try:
            return self.func == other.func and self.inst() == other.inst()
        except AttributeError:
            return False

    def __ne__(self, other):
        '''
        Inverse of __eq__.
        '''
        return not self.__eq__(other)

class CbList(list):
    def __call__(self, *args, **kwords):
        to_remove = set()
        for callback in self:
            try:
                callback(*args, **kwords)
            except ReferenceError:
                to_remove.add(callback)
        map(lambda cb: cb.unregister(), to_remove)

class CbHandler(object):
    def __init__(self, source, function):
        self.source = source
        self.function = function
    
    def __call__(self, *args, **kwords):
        return self.function(*args, **kwords)
    
    def unregister(self):
        source = self.source()
        if source is not None:
            source.unregister(self)

class CbCaller(object):
    def __init__(self):
        self._callbacks = CbList()
    
    def notify(self, *args, **kwords):
        self._callbacks(*args, **kwords)
    
    def register(self, callback):
        if inspect.ismethod(callback):
            callback = MethodeCb(callback)
        handler = CbHandler(ref(self), callback)
        self._callbacks.append(handler)
        return handler
    
    def unregister(self, handler):
        self._callbacks.remove(handler)

class Variable(CbCaller):
    def __init__(self, value=None):
        CbCaller.__init__(self)
        self._value = value
    
    def set(self, value):
        oldValue = self._value
        self._value = value
        CbCaller.notify(self, self, oldValue)
        
    def notify(self):
        CbCaller.notify(self, self, self)
    
    def get(self):
        return self._value
    
    def __str__(self):
        return str(self.get())
    
    def __repr__(self):
        return "< Variatic : [%s] >" % str(self)

class ProxyVar(Variable):
    def __init__(self, var, getcall):
        Variable.__init__(self, getcall)
        self.var = var
        var.register(self.on_change)
    
    def on_change(self, var, old):
        CbCaller.notify(self, var, old)
    
    def set(self, value):
        pass
    
    def get(self):
        return self._value()

default = object()

class Property(object):
    def __init__(self, doc=None, **kwords):
        self.fget = kwords.get('fget', default)
        self.fset = kwords.get('fset', default)
        self.fdel = kwords.get('fdel', default)
        self.doc  = doc

    def create_objects(self, name):
        doc = self.doc
        if doc is None:
            doc = "Property %s"%name
        name = "_"+name

        var = Variable()
        fget = self.fget
        if fget is default:
            def fget(self_):
                return var.get()
        fset = self.fset
        if fset is default:
            def fset(self_, value):
                return var.set(value)
        fdel = self.fdel
        if fdel is default:
            def fdel(self_):
                delattr(self_, name)
        def notify(self_):
            """make the var notify has it where changed"""
            return var.notify()
        def register(self_, callback):
            """register a callback for change of the variable"""
            return var.register(callback)
        def unregister(self_, handler):
            """unregister a callback for change of the variable"""
            return var.unregister(handler)
        return (var, fget, fset, fdel, doc, notify, register, unregister)


class HasPropertyMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "HasProperty":
            return type.__new__(cls, name, bases, dct)

        newdct = {}
        for attrName, attr in dct.items():
            if not isinstance(attr, Property):
                newdct[attrName] = attr
                continue
            var, fget, fset, fdel, doc, notify, register, unregister = attr.create_objects(attrName)
            newdct[attrName] = property(fget, fset, fdel, doc)
            newdct["_%s"%attrName] = var
            newdct["%s_notify"%attrName] = var.notify
            newdct["%s_register"%attrName] = var.register
            newdct["%s_unregister"%attrName] = var.unregister

        return type.__new__(cls, name, bases, newdct)

class HasProperty(object):
    __metaclass__ = HasPropertyMeta

