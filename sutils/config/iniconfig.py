"""read_config.py

Implements reading the config file.
"""

from ..utils import ini
from .configoptions import parser as config_parser
from ..configparse.configparse import get_description_dict, get_default_dict


def read(path):
    config_dict = ini.ini2dict(path)
    parsed_config = config_parser.parse_config(config_dict)

    return parsed_config

def write(config, path, desc):
    ini.dict2ini(config, path, desc)

def write_default(path):
    desc = get_description_dict(config_parser)
    defaults = get_default_dict(config_parser)

    write(defaults, path, desc)
