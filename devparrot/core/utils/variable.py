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


import types

from weakref import ref
import inspect

class MethodeCb:
    def __init__(self, mtd):
        try:
            try:
                self.inst = ref(mtd.__self__)
            except TypeError:
                self.inst = None
            self.func = mtd.__func__
        except AttributeError:
            self.inst = None
            self.func = mtd.__func__
    
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
            mtd = types.MethodType(self.func, inst)
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
        [cb.unregister() for cb in to_remove]

class CbHandler:
    def __init__(self, source, function):
        self.source = source
        self.function = function
    
    def __call__(self, *args, **kwords):
        return self.function(*args, **kwords)
    
    def unregister(self):
        source = self.source()
        if source is not None:
            source.unregister(self)

class CbCaller:
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

class Property:
    def __init__(self, doc=None, **kwords):
        self.fget = kwords.get('fget', default)
        self.fset = kwords.get('fset', default)
        self.fdel = kwords.get('fdel', default)
        self.doc  = doc

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError

        if self.fget is None:
            raise AttributeError

        if self.fget is not default:
            return self.fget(instance)
        return getattr(instance, self.name).get()

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError

        if self.fset is None:
            raise AttributeError

        if self.fset is not default:
            return self.fset(instance, value)
        return getattr(instance, self.name).set(value)

    def __delete__(self, instance):
        if instance is None:
            raise AttributeError

        if self.fdel is None:
            raise AttributeError

        if self.fdel is not default:
            return self.fdel(instance)
        return delattr(instance, self.name)

class HasPropertyMeta(type):
    def __new__(cls, name, bases, dct):
        if name == "HasProperty":
            return type.__new__(cls, name, bases, dct)

        property_list = []
        newdct = {'_HasProperty__property_list': property_list}
        for attrName, attr in dct.items():
            newdct[attrName] = attr
            if isinstance(attr, Property):
                attr.name = "_%s"%attrName
                newdct["%s_notify"%attrName] = lambda s, n="_%s"%attrName: getattr(s, n).notify()
                newdct["%s_register"%attrName] = lambda s, cb, n="_%s"%attrName: getattr(s, n).register(cb)
                newdct["%s_unregister"%attrName] = lambda s, hd, n="_%s"%attrName: getattr(s, n).unregister(hd)
                property_list.append(attrName)

        return type.__new__(cls, name, bases, newdct)

class HasProperty(metaclass=HasPropertyMeta):
    def __init__(self):
        for name in self.__property_list:
            setattr(self, "_%s"%name, Variable())
