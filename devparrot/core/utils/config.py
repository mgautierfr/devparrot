# -*- coding: utf8 -*-
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


class Value:
    def __init__(self, option, keys):
        self.option = option
        self.keys =  keys

    def get(self):
        return self.option.get(self.keys)

    def __getitem__(self, key):
        return Value(self.option, self.keys+[key])

    def set(self, value):
        container = self.option.set_container_for(self.keys)
        container[None] = value

    def __setitem__(self, key, value):
        container = self.option.set_container_for(self.keys+[key])
        container[None] = value


class ReadOnlyOption:
    def __init__(self, name, config, parent, type, value):
        self._init_option(name, config, parent, type)
        self.values[None] = value

    def _init_option(self, name, config, parent, type):
        self.name = name
        self.config = config
        self.parent = parent
        self.type = type
        self.values = {}

    @classmethod
    def _get_value(cls, valueDict, keys):
        if not keys:
            return valueDict[None]
        k, left = keys[0], keys[1:]
        while True:
            if k is None:
                return valueDict[None]

            try:
                subValueDict = valueDict[k]
                return cls._get_value(subValueDict, left)
            except KeyError:
                pass
            try:
                k, left = left[0], left[1:]
            except IndexError:
                return valueDict[None]

    def __getitem__(self, key):
        return self.get_value([key])

    def get(self, keys=None):
        return self._get_value(self.values, keys)

    def get_value(self, keys=None):
        return ReadOnlyValue(self, keys)

    def __str__(self):
        def get_str(value):
            if isinstance(value, dict):
                return str({k:get_str(v) for k,v in value.items()})
            return str(value)
        return get_str(self.values)

    def get_dict(self):
        def get_val(value):
            if isinstance(value, dict):
                return {k:get_val(v) for k,v in value.items()}
            return value
        return get_val(self.values)

class Option(ReadOnlyOption):
    def __init__(self, name, config, parent, type):
        self._init_option(name, config, parent, type)

    @property
    def full_name(self):
        return "%s%s"%(self.parent.full_name, self.name)

    @classmethod
    def _set_dict_container(cls, valueDict, keys):
        if not keys or keys[0] is None:
            return valueDict
        return cls._set_dict_container(valueDict.setdefault(keys[0], {}), keys[1:])

    def set_container_for(self, keys):
        return self._set_dict_container(self.values, keys)

    def __setitem__(self, key, value):
        self.set([key], value)

    def get_value(self, keys=None):
        return Value(self, keys)

    def set(self, value, keys=None):
        self.set_container_for(keys)[None] = value

    def remove(self, keys):
        del self.set_container_for(keys)[None]

    def update(self, value, keys=[]):
        if not isinstance(value, dict):
            self.set(value, keys)
        else:
            for k, v in value.items():
                self.update(v, keys+[k])

class BaseSection:
    def __init__(self, config):
        self.options = {}
        self.config = config
        

    def _get(self, name):
        return self.options[name]

    def __contains__(self, name):
        return name in self.options

    def add_option(self, name, type=str, **kwords):
        self.options[name] = Option(name, self.config, self, type)
        if "default" in kwords:
            self.options[name].set(kwords["default"])
        return self.options[name]

    def add_section(self, name):
        self.options[name] = Section(self.config, self, name)
        return self.options[name]

    def update(self, options, in_keys=[], skip_unknown=False):
        for key, value in options.items():
            if key[0] == "_":
                continue
            try:
                self._get(key).update(value, in_keys)
            except KeyError:
                if not skip_unknown:
                    raise
                print("%s is not a valid option name"%key)

    def _debug_dump(self):
        for k, v in self.options.items():
            print("key :", k)
            print(str(v))

    def __getattr__(self, name):        
        return self._get(name)

    def __setattr__(self, name, value):
        if name == "options":
            object.__setattr__(self, name, value)
            return
        if name in self.options:
            self.options[name].set(value)
        else:
            return object.__setattr__(self, name, value)

class Section(BaseSection):
    def __init__(self, config, parent, name):
        BaseSection.__init__(self, config)
        self.parent = parent
        self.name = name

    @property
    def full_name(self):
        return "%s%s."%(self.parent.full_name, self.name)

class AutoCreateSection(Section):
    def __init__(self, config, parent, name):
        BaseSection.__init__(self, config)
        self.parent = parent
        self.name = name

    def _get(self, name):
        try:
            return self.options[name]
        except KeyError:
            self.add_option(name)
            return self.options[name]

class Config(BaseSection):
    def __init__(self):
        BaseSection.__init__(self, self)

    @property
    def full_name(self):
        return ""

    def get_option(self, name):
        names = name.split('.')
        sections, name = names[:-1], names[-1]
        section = self
        for sectionName in sections:
            section = section._get(sectionName)
        return section._get(name)

    def get(self, name, keys=None):
        option = self.get_option(name)
        return option.get(keys)

    def __getattr__(self, name):
        return self._get(name)

    __getitem__ = __getattr__


class ProxySection(dict):
    def __init__(self, section):
        dict.__init__(self)
        self._section = section

    def __getitem__(self, name):
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            if name in self._section.options:
                proxy = ProxySection(self._section.options[name])
                self[name] = proxy
                return proxy
        raise KeyError

    def __setitem__(self, name, v):
        dict.__setitem__(self,name, v)

    def _has_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, ProxySection):
                d[k] = v._has_dict()
            else:
                d[k] = v
        return d

class ChaineDict:
    def __init__(self, globals_, options):
        self.globals = globals_
        self.options = options

    def __getitem__(self, name):
        try:
            return self.globals[name]
        except KeyError:
            return self.options[name]

    def __setitem__(self, name, v):
        if name in self.globals:
            self.globals[name] = v
        else:
            self.options[name] = v

class ConfigFile:
    def __init__(self, filename):
        self.filename = filename

    def parse(self, config, with_dict):
        options = ProxySection(config)
        #globals_ = {'source' : self.source_file}
        globals_ = with_dict
        exec(compile(open(self.filename).read(), self.filename, 'exec'), {}, ChaineDict(globals_, options))
        return options._has_dict()

    def source_file(self, filename):
        pass

class ConfigParser:
    def __init__(self, config):
        self.config = config
        self.configFiles = []

    def add_file(self, filename):
        self.configFiles.append(ConfigFile(filename))

    def parse(self, in_keys=[], with_dict={}):
        for configFile in self.configFiles:
            options = configFile.parse(self.config, with_dict)
            self.config.update(options, in_keys, skip_unknown=True)
