"""
This module implements functions for handling of ini files. That is, files of the type:

    [section1]
    attr1 = val1
    attr2 = val2

    [section2]
    attr1 = val1

    .
    .
    .

can be read and transformed into a list of dictionaries.

As an easy method to set up Parameters instances, an interface is implemented to create an
instance from such an ini file. The section name must be `par-<parameter_name>`, and the required attributes are `hi`, `lo`, `step`, for upper, lower bounds and stepsize of the grid.

Line comments:
Sequences following a semicolon ; are ignored.

End data section:
Everything following a line ';;;' is ignored.

"""
import sys
import os
PY_VERSION = sys.version
if int(PY_VERSION[0]) < 3:
    import exceptions
import numpy as np
from . import parameters
from . import util

class IniFormatError(Exception):
    """
    Raised when there is a format error within the ini file. Check the documentation above for the format specifications.
    """
    def __init__(self, value):
        self._value = value
    
    def __str__(self):
        return self._value

class SectionError(Exception):
    pass

class AttributeError(Exception):
    pass


def parse_line(line):
    """Parse a single line.

    :return result: str if the line contains a section header,
                    tuple if the line contains an attribute assignement,
                    None otherwise (empty lines, comments)
    :rtype result: str, tuple, None
    """
    tmp = line.split(';')[0].strip()    # ignore comments (everything after ;)
    if tmp.startswith('['):
        # section header
        if not tmp.endswith(']'):
            raise SectionError
        name = tmp[1:-1]    # section name
        return name
    elif "=" in tmp:
        if tmp.count("=") > 1:
            raise AttributeError
        tmp = tmp.split("=")
        name = tmp[0].strip()
        value = tmp[1].strip()
        return (name, value)
    elif len(tmp) > 0:
        raise IniFormatError
    else:
        return None

def ini2dict(path):
    """Read ini file and output attributes in a dictionary.
    Each key will refer to one section, which is stored in its own dictionary as the value.
    """
    data = dict()
    cur_section = None
    with open(path, 'r') as ini_file:
        for line_number,line in enumerate(ini_file):
            try:
                res = parse_line(line)
            except SectionError:
                raise IniFormatError(
                    "Section didn't end properly. Must be enclosed in [<section>]: {line:s}, line: {line_number:d}" \
                    .format(
                        line=line,
                        line_number=line_number
                        )
                    )
            except AttributeError:
                raise IniFormatError(
                    "Line {}: Couldn't interpret line as (attribute, value) pair. Make sure to use the format `attr = val`." \
                    .format(line_number)
                )
            except IniFormatError:
                raise IniFormatError(
                    "Line {}: Invalid syntax. Value: `{}`".format(line_number, line)
                )
            
            if res is None:
                # empty line or comment
                pass
            elif isinstance(res, str):
                # new section header
                data[res] = dict()
                cur_section = res
            else:
                # new attribute
                if cur_section is None:
                    raise IniFormatError("Line {}: Attribute defined outside of section.".format(line_number))
                data[cur_section][res[0]] = res[1]

            if ';;;' in line:
                # ignore rest
                break
            
    return data

def dict2ini(ini_dict, path, desc=None):
    """Store data from :ini_dict: to ini file :path:.
    
    :desc: can be another dict like :ini_dict: only containing descriptions instead of values.
    """

    if not isinstance(ini_dict, dict):
        raise TypeError("Dictionary expected, got {}.".format(str(type(ini_dict))))
    
    dir_path = os.path.abspath(os.path.dirname(path))  # make absolute path
    filename = os.path.basename(path)                  # filename

    if util.get_extension(filename) != 'ini':
        filename += '.ini'

    with open(os.path.join(dir_path, filename), 'w') as outfile:
        for section, attributes in ini_dict.items():
            outfile.write("[{}]\n".format(section))
            for attr_name, attr_value in attributes.items():
                try:
                    description = desc[section][attr_name]
                except KeyError:
                    description = None
                if description is None:
                    outfile.write("{name}={value}\n".format(
                                                            name=attr_name,
                                                            value=attr_value,
                                                            )
                            )
                else:
                    outfile.write("{name}={value}{space};{desc}\n".format(
                                                            name=attr_name,
                                                            value=attr_value,
                                                            space=" "*10,
                                                            desc=description
                                                            )
                            )
            outfile.write("\n") # newline


def read_ini(path):
    """
    Read ini file and output attributes in a list of dictionaries.
    Each section will produce one dictionary.

    """
    active_sec = -1
    attr_cache, val_cache = [], []
    dicts = []
    with open(path, 'r') as ini_file:
        for line_number,line in enumerate(ini_file):
            if ';;;' in line:
                # ignore rest
                break
            elif ";" in line:
                s_line = line.split(";")[0] # ignore comments
            else:
                s_line = line
            s_line = s_line.strip()
            if s_line.startswith('['):
                if not s_line.endswith(']'):
                    raise IniFormatError("Section didn't end properly. Must be enclosed in [<section>]: {line:s}, line: {line_number:d}".format(line=line, line_number=line_number))
                    
                section = s_line[1:-1]
                dicts.append(dict([('name', section)]))

                active_sec += 1
            elif line in ['\n', ''] or s_line in ['\n', '']:
                # skip empty lines
                pass
            elif line.strip() == ';;;':
                break
            else:
                #print(line, s_line)
                try:
                    attr, val = [a.strip() for a in s_line.split('=')]
                    dicts[active_sec][attr] = val
                except:
                    #print(attr, val)
                    raise IniFormatError("Couldn't interpret line as (attribute, value) pair. Make sure to use the format `attr = val`:\n{}".format(line))

    return dicts

def parameters_from_ini(path):
    """
    Create a parameters instance from ini configuration file.
    """

    attr_list = read_ini(path)

    pcfg_found = False
    general_ind = []
    pcfg_ind = None
    for ind,d in enumerate(attr_list):
        #print d['name']
        if d['name'].lower() == 'general':
            general_ind.append(ind)
            if 'other_files' in d:
                d.update({'other_files': str2list(d['other_files']),})
            if 'use_index' in d:
                d.update({'use_index': str2bool(d['use_index']),})
            if 'test_mode' in d:
                d['test_mode'] = str2bool(d['test_mode'])
            if 'overwrite_dir' in d:
                d['overwrite_dir'] = str2bool(d['overwrite_dir'])
            if 'write_parameter_info' in d:
                d['write_parameter_info'] = str2bool(d['write_parameter_info'])
        elif d['name'].lower() == 'pconfig':
            pcfg = d # create a local copy of the parameter settings dictionary
            pcfg.pop('name') # remove name key
            if 'maxdecimals' in pcfg:
                try:
                    pcfg['maxdecimals'] = int(pcfg['maxdecimals'])
                except ValueError:
                    if pcfg['maxdecimals'].lower() == 'none':
                        pcfg['maxdecimals'] = None
                    else:
                        raise ValueError("Invalid value: " + pcfg['maxdecimals'] + " for attribute 'maxdecimals'.")
            pcfg_found = True
            pcfg_ind = ind
            
    assert len(general_ind) in [0,1]

    num_par = len(attr_list) - len(general_ind) - int(pcfg_found)

    p_data = []
    for ind, d in enumerate(attr_list):
        if ind in general_ind or ind == pcfg_ind:
            pass
        else:
            if d.get('name').startswith('par-'):
                if (not 'type' in d) or d.get('type').lower() == 'scalar':
                    if 'value' in d:
                        vals = d.get('value').split(',')
                        if len(vals) == 1:
                            num = 1
                            #d.update([('lo', float(d.get('value'))), ('hi', float(d.get('value')) + 1), ('step', 1)])
                            try:
                                vals = [int(v) for v in vals]
                            except:
                                vals = [float(v) for v in vals]
                            vals = np.array(vals) #np.linspace(d.get('lo'), d.get('hi'), num)
                        else:
                            vals = np.asarray(vals).astype(np.float64)
                    elif 'values' in d:
                        vals = d.get('values').split(',')
                        vals = np.asarray(vals).astype(np.float64)
                    else:
                        assert 'hi' in d, "Value `hi` not specified for parameter %s" % d.get('name')
                        d['hi'] = float(d.get('hi'))
                        assert 'lo' in d, "Value `lo` not specified for parameter %s" % d.get('name')
                        d['lo'] = float(d.get('lo'))
                        if 'step' in d:
                            d['step'] = float(d.get('step'))
                            num = int((d.get('hi') - d.get('lo')) / d.get('step') + 1)
                        else:
                            assert 'points' in d, "Neither value `step` nor `points` specified for parameter %s" % d.get('name')
                            d['points'] = float(d.get('points'))
                            num = d['points']

                        vals = np.linspace(d.get('lo'), d.get('hi'), num)
                else:
                    if d.get('type').lower() == 'vector':
                        if 'value' in d:
                            vals = d.get('value').split(',')
                            vals = np.asarray([vals]).astype(np.float64)
                        elif 'values' in d:
                            vals = split_vector_sequence(d.get('values'))
                            vals = np.asarray([vals]).astype(np.float64)
                        else:
                            assert 'hi' in d, "Value `hi` not specified for parameter %s" % d.get('name')
                            assert 'lo' in d, "Value `lo` not specified for parameter %s" % d.get('name')
                            if 'step' in d:
                                d['step'] = float(d.get('step'))
                                num = int((d.get('hi') - d.get('lo')) / d.get('step') + 1)
                            else:
                                assert 'points' in d, "Neither value `step` nor `points` specified for parameter %s" % d.get('name')
                                d['points'] = float(d.get('points'))
                                num = d['points']
                            hi = d.get('hi')
                            lo = d.get('lo')
                            vals = []
                            raise NotImplementedError
                            for hi_val, lo_val in zip(hi, lo):
                                vals.append(np.linspace(lo_val, hi_val, num))
                            
                            vals = np.linspace(d.get('lo'), d.get('hi'), num)

                name = d.get('name').split('-')[-1]
                p_data.append(parameters.Parameter(name, vals))

    p = parameters.Parameters(p_data, **pcfg)

    return p, attr_list[general_ind[0]]


def split_vector_sequence(s):
    """
    Interpret a string as a sequence of vectors, return the vectors.
    """
    vec_s_list = s.split(")")
    vec_list = []
    dim = None
    for vs in vec_s_list:
        vs = vs.split('(')[1]
        vs = vs.split(',')
        if dim is None:
            pass
        else:
            if dim != len(vs):
                raise ValueError("Not all vectors have the same dimension!")
        vec_list.append(np.array([float(val) for val in vs]))
    
    return vec_list

def str2list(s):
    """Convert a string to a list.

    An input "a,b,c" would be converted to ['a', 'b', 'c'].
    Commas separate different entries.
    Type conversion is not done.
    """
    return [e.strip() for e in s.split(',')]

def str2bool(s):
    """Convert string to bool."""
    return s.strip().lower() == "true"

def make_ini_file(lst, dest):
    """Save `lst` as an ini file to `dest`."""
    with open(dest, "w") as outfile:
        for grp in lst:
            outfile.write("[{}]".format(grp.name), end="\n")
            for opt in grp.members:
                outfile.write("{} = {} {}".format(opt.name, opt.default_value, opt.description), end="\n")
            outfile.write("\n")
        