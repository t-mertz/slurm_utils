import sys
from ...utils import ini,util
import numpy as np

def get_config():
    """Return the essential configuration specifics, i.e. number of parameters,
    total number of jobs..
    """
    if not util.fexists('config.ini'):
        print("Can't find file: config.ini")
        sys.exit(1)
    
    params, settings = ini.parameters_from_ini('config.ini')

    return params, settings

def get_number_params():
    return get_config()[0].get_dim()

def get_number_jobs():
    return get_config()[0].get_maxnum()

def get_parameter_info(parameter_name=None):
    params, settings = get_config()
    names = params.get_names()

    if parameter_name == None:
        # all
#        value_format = " | ".join(["{:3d} - {:10}"]*len(names))
        value_format = "{:3d} - {:10}"
        empty_format = " "*16
        name_format = " | ".join(["{:^16}"]*len(names))
        values = [params.get_values_ax(n) for n in names]
        print(name_format.format(*names))
        print("-|-".join(["-"*16]*len(names)))
        dims = [len(v) for v in values]
        for i in range(max(dims)):
#            cur_vals = [v[i] if i < dims[ind] else "" for ind,v in enumerate(values)]
#            line_values = []
#            for v in cur_vals:
#                line_values.append(i)
#                line_values.append(v)
#            print(value_format.format(*line_values))
            line_strings = [value_format.format(i, v[i]) if i < dims[ind] else empty_format for ind,v in enumerate(values)]
            print(" | ".join(line_strings))
        print("Total number: {}".format(np.prod(dims)))
    else:
        try:
            ind = names.index(parameter_name)
        except ValueError:
            print("Unknown parameter: {}".format(parameter_name))
            sys.exit(1)
        value_format = "{:3d} - {:10}"
        name_format = "{:16}"
        values = params.get_values_ax(names[ind])
        for i,v in enumerate(values):
            print(value_format.format(i, v))
    