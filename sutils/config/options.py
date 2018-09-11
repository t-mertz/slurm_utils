"""options.py
This file is part of sutils

Implements configuration options.
"""
import exceptions
import warnings

warnings.warn(
    "Module options is deprecated. Use configoptions instead",
    DeprecationWarning
)

GROUPS_ = {
    'general': GeneralGroup,
}

OPTIONS_ = [

]


# exceptions

class UnknownConfigOptionError(exceptions.Exception):
    pass

# end exceptions

###############################################################################

# groups

class BaseConfigGroup(object):
    pass

class ConfigGroup(BaseConfigGroup):
    name = u""
    members = (,)

class GeneralGroup(ConfigGroup):
    name = u"general"
    members = (,)

class ParameterGroup(ConfigGroup):
    pass

###############################################################################

# end groups

###############################################################################

# options

class BaseConfigOption(object):
    pass

class ConfigOption(BaseConfigOption):
    group = GeneralGroup
    name = u""
    values = ()
    default_value = None
    description = u""

    def parse(self, value_str):
        pass


class ScriptPathOption(ConfigOption):
    name = u"script_path"
    default_value = u"slurm.sh"
    description = u"path of the script file (will be submitted to SLURM via sbatch)"

    def parse(self, value_str):
        return value_str

class DirnameParametersOption(ConfigOption):
    name = u"par_in_dirname"

class OverwriteDirOption(ConfigOption):
    name = u"overwrite_dir"

class SubmitTypeOption(ConfigOption):
    name = u"submit_as"

class CmdArgumentsOption(ConfigOption):
    name = u"cmd_arguments"

class JobnamePrefixOption(ConfigOption):
    name = u"jobname_prefix"

class LogfileNameOption(ConfigOption):
    name = u"logfile_name"

class WriteParameterInfoOption(ConfigOption):
    name = u"write_parameter_info"

class TestModeOption(ConfigOption):
    name = u"test_mode"


# end options

###############################################################################

GeneralGroup.members = (
    ScriptPathOption,
    DirnameParametersOption,
    OverwriteDirOption,
    SubmitTypeOption,
    CmdArgumentsOption,
    JobnamePrefixOption,
    LogfileNameOption,
    WriteParameterInfoOption,
    TestModeOption,
)


def get_group(group_name):
    return GROUPS_['group_name']

def parse_option(group_name, option_name, value_str):
    """Parse an option using its name and value as string.
    
    Raises UnknownConfigOptionError if name is unknown.
    """
    group = get_group(group_name)
    if option_name in group.members:
        return group.members[option_name].parse(value_str)
    else:
        raise UnknownConfigOptionError(groupname + "." + "option_name")


def get_default_options():
    """Return the list of all options."""
    return GROUPS_.itervalues()
