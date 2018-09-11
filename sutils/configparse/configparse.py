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
    def __init__(self, name, type, default=None, valid_values=None, desc=None, required=False):
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
        return self._type
    
    def get_default(self):
        return self._default

    def get_valid_values(self):
        return self._valid_values
    
    def get_desc(self):
        return self._desc

    def parse(self, value):
        return self._type(value).value()

# groups

class _OptionsContainer(object):
    def __init__(self):
        super(_OptionsContainer, self).__init__()

        self._options = dict()
        self._optionsmap = dict()  # we add all options (also from groups) here
        self._groups = []
        
        self._required = False

        self._conflicts_map = dict()
    
    def is_required(self):
        return self._required

    def _add_option(self, option):
        name = option.get_name()
        if name not in self._optionsmap:
            self._options[name] = option
            self._optionsmap[name] = option
            self._required |= option.is_required()
        else:
            raise RuntimeError("Name {} already defined.".format(name))
    
    def add_option(self, name, type, default=None, valid_values=None, desc=None, required=False):
        """Add an option."""
        option = ConfigOption(name, type, default, valid_values, desc, required)
        self._add_option(option)

        return self
    
    def add_group(self):
        """Add and return a group."""
        group = _OptionsGroup(self)
        self._groups.append(group)
        
        return group

    def add_mutually_exclusive_group(self):
        group = _MutuallyExclusiveGroup(self)
        self._groups.append(group)

        return group
    
    def _check_conflicts(self, input_map):
        """This does nothing in the general case."""
        pass

    def __getitem__(self, key):
        if key not in self._optionsmap:
            raise KeyError("Unknown name {}.".format(key))
        return self._optionsmap[key]
                
    def __contains__(self, key):
        return key in self._optionsmap
    
    def __iter__(self):
        for key in self._optionsmap:
            yield self._optionsmap[key]

class _OptionsGroup(_OptionsContainer):
    def __init__(self, container):
        super(_OptionsGroup, self).__init__()

        self._optionsmap = container._optionsmap
    
    def _add_option(self, option):
        super(_OptionsGroup, self)._add_option(option)
        

class _MutuallyExclusiveGroup(_OptionsGroup):
    def __init__(self, container):
        super(_MutuallyExclusiveGroup, self).__init__(container)

        self._conflicts_map = dict()

    def _add_option(self, option):
        super(_MutuallyExclusiveGroup, self)._add_option(option)
        option_name = option.get_name()
        # add new option as conflict to others
        for opt in self._options:
            self._conflicts_map.setdefault(opt, [])
            self._conflicts_map[opt].append(option_name)
        
        # add other options as conflicts to new option
        self._conflicts_map[option_name] = self._options.keys()
    
    def add_option(self, name, type, valid_values=None, desc=None):
        """Add an option."""
        option = ConfigOption(name, type, default=None, valid_values=valid_values, desc=desc, required=False)
        self._add_option(option)

        return self

    def _check_conflicts(self, input_map):
        for name in input_map:
            if name in self._conflicts_map:
                for conf_name in self._conflicts_map[name]:
                    if conf_name in input_map:
                        raise RuntimeError("Conflicting options: {}, {}".format(name, conf_name))
            


class ConfigSection(_OptionsContainer):
    """Container for a section in an .ini file. Can contain many options and option groups."""

    def __init__(self, name, required=False):
        super(ConfigSection, self).__init__()

        self._name = name
        self._required = required
    
    def get_name(self):
        return self._name
    
    def get_default(self):
        tmp = dict()
        for name, opt in self._optionsmap.items():
            tmp[name] = opt.get_default()
        
        return tmp
    
    def _check_conflicts(self, input_map):
        for group in self._groups:
            group._check_conflicts(input_map)

    def _parse(self, input_map):
        self._check_conflicts(input_map)

        # first go through the input
        for key, val in input_map.items():
            if self.__contains__(key):
                input_map[key] = self._optionsmap[key].parse(val)
            else:
                raise RuntimeError("Unknown option: {}".format(key))

        # now add defaults
        for option_name,option in self._options.items():
            if option_name not in input_map and option.is_required():
                raise RuntimeError("Required setting {}.{} not set.".format(self._name, option_name))
            else:
                input_map.setdefault(option_name, option.get_default())
        
        for group in self._groups:
            if isinstance(group, _MutuallyExclusiveGroup):
                num_set = 0
                for option_name in group:
                    num_set += option_name in input_map
                if num_set > 1:
                    raise RuntimeError("Mutually exclusive options set.")
            else:
                for option_name, option in group:
                    if option_name not in input_map and option.is_required():
                        raise RuntimeError("Required setting {}.{} not set.".format(self._name, option_name))
                    else:
                        input_map.setdefault(option_name, option.get_default())

    def options(self):
        return self._options.items()

# class ConfigGroup(object):
#     def __init__(self, required=True):
#         #self._name = name
#         self._options = dict()
#         self._groups = []
#         self._required = required
    
#     def add_option(self, name, type, default=None, valid_values=None, desc=None, required=True):
#         """Add an option to the group."""
        
#         if name not in self._options:
#             self._options[name] = ConfigOption(name, type, default, valid_values, desc, required)
#         else:
#             raise RuntimeError("Name {} already defined.".format(name))

#         return self
    
#     def is_required(self):
#         return self._required

#     def get_default(self):
#         tmp = dict()
#         for name, opt in self._options.items():
#             tmp[name] = opt.get_default()
        
#         return tmp

#     def options(self):
#         return self._options.items()
    
#     def __getitem__(self, key):
#         return self._options[key]

#     def __contains__(self, key):
#         return key in self._options
    
#     def __iter__(self):
#         for key in self._options:
#             yield self._options[key]


# class MutuallyExclusiveGroup(ConfigGroup):
#     """No two options can be set at the same time."""
#     def __init__(self, name, required=True):
#         super(MutuallyExclusiveGroup, self).__init__(name, required)
#         self._set = None # this will set to the option that is parsed first
    
#     def set(self, option):
#         if self._set is None:
#             self._set = option
#         else:
#             raise RuntimeError("Trying to set mutually exclusive options {}, {}".format(
#                 self._set, option
#             ))

#     def reset(self):
#         """Clear cache. Allow parsing again."""
#         self._set = None

# parser

class ConfigParser(object):
    def __init__(self):
        self._sections = dict()
    
    def sections(self):
        return self._sections.items()
    
    def add_section(self, section):
        """Add a section to the parser."""
        if isinstance(section, ConfigSection):
            if section.get_name() not in self._sections:
                self._sections[section.get_name()] = section
            else:
                raise RuntimeError("Name {} already defined.".format(section.get_name()))
        else:
            raise TypeError("section must be ConfigSection, not {}.".format(str(type(section))))
        
        return self

    def parse_config(self, input_map):
        if not isinstance(input_map, dict):
            raise TypeError("Input must be dict.")
        
        output = copy.deepcopy(input_map)

        for section_name, section in output.items():
            if section_name in self._sections:
                self._sections[section_name]._parse(section)
            else:
                raise RuntimeError("Unknown section: %s" % section_name)

        # add defaults for missing sections
        for section_name, section in self._sections.items():
            if section_name not in output:
                output.update({section_name: section.get_default()})
        
        return output
            
# class ConfigParser(object):
#     def __init__(self):
#         self._groups = dict()

#     def groups(self):
#         return self._groups.items()

#     def add_group(self, group):
#         """Add a group to the parser."""
#         if isinstance(group, ConfigGroup):
#             if group.get_name() not in self._groups:
#                 self._groups[group.get_name()] = group
#             else:
#                 raise RuntimeError("Name {} already defined.".format(group.get_name()))
#         else:
#             raise TypeError("group must be ConfigGroup, not {}.".format(str(type(group))))
        
#         return self

#     def parse_config(self, input):
#         if not isinstance(input, dict):
#             raise TypeError("Input must be dict.")
        
#         output = copy.deepcopy(input)

#         # go through everything and parse it
#         for groupname, group in input.items():
#             if groupname in self._groups:
#                 cur_group = self._groups[groupname]
#                 for option, value in group.items():
#                     if (option != 'name') and (option in cur_group):
#                         #if isinstance(cur_group, MutuallyExclusiveGroup):
#                         #    cur_group.set(option) # mark option as set
#                         output[groupname][option] = cur_group[option].parse(value)
#                     else:
#                         raise RuntimeError("Unknown option: {}".format(option))
#             else:
#                 raise RuntimeError("Unknown section: {}".format(groupname))

#         # go through everything again and add required defaults
#         for groupname, group in self._groups.items():
#             if groupname not in output:
#                 output[groupname] = group.get_default()
#             else:
#                 for optionname, option in group.options():
#                     if optionname not in output[groupname] and option.is_required():
#                         if option.get_default() is None:
#                             raise RuntimeError("Required setting {}.{} not set.".format(groupname,optionname))
#                         output[groupname][optionname] = option.get_default()

#         return output

#     def __contains__(self, key):
#         return key in self._groups

#     def __getitem__(self, key):
#         return self._groups[key]

#     def __iter__(self):
#         for key in self._groups:
#             yield self._groups[key]


def get_default_dict(parser, required_only=True):
    """Return a dictionary of defaults."""
    retval = dict()
    for group_name, group in parser.sections():
        if group.is_required():
            retval[group_name] = dict()
            for attr_name, attr_value in group.options():
                if attr_value.is_required:
                    retval[group_name][attr_name] = attr_value.get_default()

    return retval

def get_description_dict(parser):
    """Return a dictionary of descriptions."""
    retval = dict()
    for group_name, group in parser.sections():
        retval[group_name] = dict()
        for attr_name, attr_value in group.options():
            retval[group_name][attr_name] = attr_value.get_desc()
    
    return retval
