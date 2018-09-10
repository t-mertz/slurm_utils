"""iniconfig.py

Implements reading the config file.
"""

from ..utils import ini
from .configoptions import parser as config_parser
from ..configparse.configparse import get_description_dict, get_default_dict
from . import parameterconfig


def read(path):
    config_dict = ini.ini2dict(path)
    parameter_defs = parameterconfig.split_parameters(config_dict)  # parameters need to be ignored by config parser
    parsed_config = config_parser.parse_config(config_dict)
    parsed_config['parameters'] = parameter_defs                    # adding parameters
    parameterconfig.parse_parameters(parsed_config)                 # this changes parsed_config inplace!

    return parsed_config

def write(config, path, desc):
    ini.dict2ini(config, path, desc)

def write_default(path):
    desc = get_description_dict(config_parser)
    defaults = get_default_dict(config_parser)

    write(defaults, path, desc)
