"""configparse.py

part of sutils

Here we define a parser in the spirit of argparse, which can be given different
groups containing options that are automatically parsed from string and converted
to the correct type.
"""
import os
import copy
#from .cfgtypes import *

# options

class ConfigOption(object):
    def __init__(self, name, type, default=None, valid_values=None, desc=None, required=True):
        self._name = name
        self._type = type
        self._default = default
        self._valid_values = valid_values
        self._desc = desc
        self._required = bool(required)

    def is_required(self):
        return self._required
    
    def get_name(self):
        return self._name

    def get_type(self):
        return self._name
    
    def get_default(self):
        return self._default

    def get_valid_values(self):
        return self._name
    
    def get_desc(self):
        return self._desc

    def parse(self, value):
        return self._type(value).value()

# groups

class ConfigGroup(object):
    def __init__(self, name, required=True):
        self._name = name
        self._options = dict()
        self._required = required
    
    def add_option(self, name, type, default=None, valid_values=None, desc=None, required=True):
        """Add an option to the group."""
        
        if name not in self._options:
            self._options[name] = ConfigOption(name, type, default, valid_values, desc, required)
        else:
            raise RuntimeError("Name {} already defined.".format(name))

        return self
    
    def is_required(self):
        return self._required

    def get_name(self):
        return self._name
    
    def get_default(self):
        tmp = dict()
        for name, opt in self._options.items():
            tmp[name] = opt.get_default()
        
        return tmp

    def options(self):
        return self._options.items()
    
    def __getitem__(self, key):
        return self._name if key == 'name' else self._options[key]

    def __contains__(self, key):
        return key in self._options
    
    def __iter__(self):
        for key in self._options:
            yield self._options[key]


# parser

class ConfigParser(object):
    def __init__(self):
        self._groups = dict()

    def groups(self):
        return self._groups.items()

    def add_group(self, group):
        """Add a group to the parser."""
        if isinstance(group, ConfigGroup):
            if group.get_name() not in self._groups:
                self._groups[group.get_name()] = group
            else:
                raise RuntimeError("Name {} already defined.".format(group.get_name()))
        else:
            raise TypeError("group must be ConfigGroup, not {}.".format(str(type(group))))
        
        return self

    def parse_config(self, input):
        if not isinstance(input, dict):
            raise TypeError("Input must be dict.")
        
        output = copy.deepcopy(input)

        # go through everything and parse it
        for groupname, group in input.items():
            if groupname in self._groups:
                cur_group = self._groups[groupname]
                for option, value in group.items():
                    if (option != 'name') and (option in cur_group):
                        output[groupname][option] = cur_group[option].parse(value)

        # go through everything again and add required defaults
        for groupname, group in self._groups.items():
            if groupname not in output:
                output[groupname] = group.get_default()
            else:
                for optionname, option in group.options():
                    if optionname not in output[groupname] and option.is_required():
                        if option.get_default() is None:
                            raise RuntimeError("Required setting {}.{} not set.".format(groupname,optionname))
                        output[groupname][optionname] = option.get_default()

        return output

    def __contains__(self, key):
        return key in self._groups

    def __getitem__(self, key):
        return self._groups[key]

    def __iter__(self):
        for key in self._groups:
            yield self._groups[key]


def get_default_dict(parser, required_only=True):
    """Return a dictionary of defaults."""
    retval = dict()
    for group_name, group in parser.groups():
        if group.is_required():
            retval[group_name] = dict()
            for attr_name, attr_value in group.options():
                if attr_value.is_required:
                    retval[group_name][attr_name] = attr_value.get_default()

    return retval

def get_description_dict(parser):
    """Return a dictionary of descriptions."""
    retval = dict()
    for group_name, group in parser.groups():
        retval[group_name] = dict()
        for attr_name, attr_value in group.options():
            retval[group_name][attr_name] = attr_value.get_desc()
    
    return retval
