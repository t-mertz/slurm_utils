# part of sutils
import sys
from collections import OrderedDict

from ..configparse import cfgtypes
from ..parameters import numeric
from ..utils.parameters import Parameters as ParametersType
from ..utils.parameters import Parameter as ParameterType

VALUE = 1
VALUES = 2
LO = 4
HI = 8
STEP = 16
POINTS = 32

OPTIONS = {
    'value'     : VALUE,
    'values'    : VALUES,
    'lo'        : LO,
    'hi'        : HI,
    'step'      : STEP,
    'points'    : POINTS,
}

PARAMETER_TYPES = {
    'value'          : VALUE,
    'values'         : VALUES,
    'points-range'   : LO | HI | POINTS,
    'step-range'     : LO | HI | STEP,
}

class _ParameterType(object):
    def __init__(self, settings_map):
        self._settings = settings_map

    def values(self):
        pass

class ParameterValue(_ParameterType):
    def __init__(self, settings_map):
        super(ParameterValue, self).__init__(settings_map)
    
    def values(self):
        return self._settings['value']

class ParameterValues(_ParameterType):
    def __init__(self, settings_map):
        super(ParameterValues, self).__init__(settings_map)
    
    def values(self):
        return cfgtypes.StringListType(self._settings['values']).value()

class ParameterPointsrange(_ParameterType):
    def __init__(self, settings_map):
        super(ParameterPointsrange, self).__init__(settings_map)
    
    def values(self):
        lo = cfgtypes.NumericType(self._settings['lo']).value()
        hi = cfgtypes.NumericType(self._settings['hi']).value()
        points = cfgtypes.IntType(self._settings['points']).value()
        return numeric.points_range(lo, hi, points)

class ParameterSteprange(_ParameterType):
    def __init__(self, settings_map):
        super(ParameterSteprange, self).__init__(settings_map)
    
    def values(self):
        lo = cfgtypes.NumericType(self._settings['lo']).value()
        hi = cfgtypes.NumericType(self._settings['hi']).value()
        step = cfgtypes.NumericType(self._settings['step']).value()
        return numeric.step_range(lo, hi, step)

def construct_parameter(param_t, settings_map):
    """Factory function for parameter types."""
    if param_t == PARAMETER_TYPES['value']:
        return ParameterValue(settings_map)
    elif param_t == PARAMETER_TYPES['values']:
        return ParameterValues(settings_map)
    elif param_t == PARAMETER_TYPES['points-range']:
        return ParameterPointsrange(settings_map)
    elif param_t == PARAMETER_TYPES['step-range']:
        return ParameterSteprange(settings_map)
    else:
        raise ValueError("Unkown parameter type: %d" % param_t)

def get_parameter_type(parameter_dict):
    """Check if the parameter definition is valid and determine the type."""
    identifier = 0
    for key in parameter_dict:
        if key in OPTIONS:
            identifier |= OPTIONS[key]
        else:
            raise ValueError("Unkown option in parameter definition: %s" % key)

    if identifier in PARAMETER_TYPES.values():
        return identifier
    else:
        if identifier == 0:
            raise ValueError("No option set in parameter definition.")
        options_set = []
        for key, val in OPTIONS.items():
            if identifier & val:
                options_set.append(key)
        raise ValueError("Invalid combination of options in parameter definition: {}".format(", ".join(options_set)))
        

def is_parameter(name):
    """Check if a section name corresponds to a parameter definition."""
    return name.startswith('par-')

def get_parameter_name(sectionname):
    """Obtain the parameter name from the sectionname."""
    if is_parameter(sectionname):
        if len(sectionname) > 4:
            return sectionname[4:]
        else:
            raise ValueError("No parameter name specified.")
    else:
        raise ValueError("Not a parameter: %s" % sectionname)

def split_parameters(config):
    """Split parameter sections from global config."""
    parameters = OrderedDict()  # we want to remember the order of parameters
    for sectionname in config:
        if is_parameter(sectionname):
            parameters[get_parameter_name(sectionname)] = config.pop(sectionname)
    
    return parameters

def parse_parameters(config):
    """Parse the parameter options read from the ini file."""
    parameters = config['parameters']
    params = []
    for key, val in parameters.items():
        param_t = get_parameter_type(val)
        params.append(ParameterType(key, construct_parameter(param_t, val).values()))
    
    # construct parameters instance here
    params = ParametersType(params, mode=config['pconfig']['mode'], maxdecimals=config['pconfig']['maxdecimals'])

    config['parameters'] = params

    


            