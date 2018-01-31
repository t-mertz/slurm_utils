from __future__ import division
import numpy as np
import math
import os

def assert_dir(path):
    """
    Check if a path exists, if not create a directory.

    If path existed before, return True, else False.
    """
    existed = False
    if not os.access(path, os.F_OK):
        os.mkdir(path)
    else:
        existed = True

    return existed


def fexists(path):
    """
    Check if a path exists.
    """
    if os.access(path, os.F_OK):
        return True
    return False

def funiquename(path, extension=""):
    """
    Create a unique filename by appending a number separated by an underscore
    to the end of the existing filename. The first match is returned.

    If extension is supplied, it will be appended at the end of the filename.
    """
    def extend(p, e):
        return p + e

    if fexists(extend(path, extension)):
        i = 1
        while fexists(extend(path+"_{}".format(i),extension)):
            i += 1
        return extend(path + "_{}".format(i), extension)
    return extend(path, extension)

def isiterable(var):
    """
    Check if input is iterable.
    """
    return hasattr(var, "__iter__")

def isdirectory(path):
    """
    Check if input path is a directory.
    """
    try:
        cwd = os.getcwd()
        os.chdir(path)
        os.chdir(cwd)
    except OSError:
        return False

    return True

def listdirs(path):
    """
    List only directories one level lower than path in the directory tree.
    """
    filelist = os.listdir(path)

    dirlist = []
    for fname in filelist:
        if isdirectory(os.path.join(path, fname)):
            dirlist.append(fname)

    return dirlist

def listdirs_rec(path):
    """
    Recursively list directories lower than the root `path`.

    Example:
    In a directory `dir0` with subdirectories `dir00`, ..., `dir0n`, which contain
    `dir000`, ..., `dir0nm`, this function returns 
    
    listdirs_rec(`dir0`) = [`dir0/dir00`, ..., `dir0/dir0n`, `dir0/dir00/dir000`, 
    ..., `dir0/dirn/dir0nm`].
    """

    dirlist = []
    cur_dirlist = [os.path.join(path, d) for d in listdirs(path)]
    dirlist += cur_dirlist

    if len(cur_dirlist) == 0:
        pass
    else:
        for newpath in cur_dirlist:
            dirlist += listdirs_rec(newpath)

    return dirlist

def listdirs_rec_base(path):
    """
    Recursively list directories on the base level under `path`.

    Example:
    In a directory `dir0` with subdirectories `dir00`, ..., `dir0n`, which contain
    `dir000`, ..., `dir0nm`, this function returns 
    
    listdirs_rec_base(`dir0`) = [`dir0/dir00/dir000`, ..., `dir0/dir0n/dir0nm`].
    """

    dirlist = []
    cur_dirlist = [os.path.join(path, d) for d in listdirs(path)]
    
    if len(cur_dirlist) == 0:
        dirlist.append(path)
    else:
        for newpath in cur_dirlist:
            dirlist += listdirs_rec_base(newpath)

    return dirlist



def copy_replace(in_path, out_path, pattern, subst):
    """
    Replace all occurrences of `pattern` in file `in_path` by `subst` and
    save the copy to `out_path`.
    `pattern` and `subst` can be iterable.
    """
    if hasattr(pattern, '__iter__'):
        iterable = True
        num_patterns = len(pattern)
    else: iterable = False

    if not iterable:
        with open(in_path, 'r') as input_file:
            with open(out_path, 'w') as output_file:
                for line in input_file:
                    output_file.write(line.replace(pattern, subst))

    else:
        with open(in_path, 'r') as input_file:
            with open(out_path, 'w') as output_file:
                for line in input_file:
                    replace_itms = 0
                    pattern_itm = pattern[0]
                    subst_itm = subst[0]
                    for p,s in zip(pattern, subst):
                        if p in line:
                            replace_itms += 1
                            pattern_itm = p
                            subst_itm = s
                    if replace_itms > 1:
                        raise RuntimeError("Warning possible conflict!")
                    output_file.write(line.replace(pattern_itm, subst_itm))

def generate_format_spec(num_vals, sep, dtypes, decimals=None):
    """
    Generate a format specifier for generic input.
    
    --------------------------------------------------------------
    
    Input
    
    num_vals : number of wild-cards
    sep      : separator string (could be '_', '-', '--' ...)
               used to separate wild-cards
    dtypes   : data types of the wildcards ('str', 'float', 'int')
    decimals : number of decimals (only relevant for floats)
    
    --------------------------------------------------------------
    
    Output
    
    String of the form: "{0:<dtype>}<sep>{1:<dtype>}<sep>...",
    where each occurrence of <dtype> is replaced by the dtype value of
    the current wild-card and <sep> is replaced by the separator string. 
    """
    assert type(num_vals) is int
    
    # dictionary of identifiers for supported data types
    dident = dict([(str, 's'),
                   (int, 'd'), \
                   (np.int32, 'd'), \
                   (np.int64, 'd'), \
                   (float, ''), #'.1f'\
                   (np.float64, '') #'.1f'
                  ]
                 )
    if decimals is not None:
        assert type(decimals) is int
        dident[float] = '.{}f'.format(decimals)
        dident[np.float64] = '.{}f'.format(decimals)
                 
    if not hasattr(dtypes, '__iter__'):
        dtypes = [dtypes,] * num_vals
    elif type(dtypes) is str:
        dtypes = [dtypes,] * num_vals
    elif len(dtypes) < num_vals:
        dtypes = [dtypes[0],] * num_vals
         
    for dt in dtypes:
        assert dt in dident.keys(), dt
    
    # construct actual output
    out = ""
    for i in range(num_vals):
        out += "{" + str(i) + ":" + dident[dtypes[i]] + "}"
        out += sep
    
    # remove additional separator from output
    return out[:-len(sep)]


def generate_named_index_format_spec(parameters, sep, sep1=""):
    """
    Generate a format specifier for generic input.
    
    --------------------------------------------------------------
    
    Input
    
    parameters : names of the parameters to appear in the formatter
    sep        : separator string (could be '_', '-', '--' ...)
                 used to separate wild-cards

    --------------------------------------------------------------
    
    Output
    
    String of the form: "<parameters1><sep1>{0:d}<sep><parameters2><sep1>{1:d}<sep>...",
    where each occurrence of <sep> is replaced by the separator string. 
    """
    num_vals = len(parameters)

    # construct actual output
    out = ""
    for i, pval in enumerate(parameters):
        out += pval
        out += sep1
        out += "{" + str(i) + ":" + "d" + "}"
        out += sep
    
    # remove additional separator from output
    return out[:-len(sep)]

def find_decimals(value, maxlen=10):
    """
    Find the decimal representation of `value`.

    `maxlen` is the maximal number of digits.
    """
    e = np.floor(np.log10(value)) # exponent
    b = [] # list of decimals
    new_rep = 0
    vi = value
    i = 0
    while abs(new_rep - value) > 1e-10:
        bi = np.floor(vi / 10**(e-i))
        b.append(int(bi))
        vi = vi - b[-1] * 10**(e-i)
        new_rep = sum([bv * 10**(e-bj) for bj, bv in enumerate(b)])
        #print new_rep
        i += 1
        if i >= 100:
            break

    if new_rep - value > 0:
        b[-1] = b[-1] - 1 if b[-1] > 0 else 0
    elif new_rep - value < 0:
        i = 0
        for bv in b[::-1]:
            if bv != 9:
                break
            i += 1
        b[-i-1] = b[-i-1] + 1
        b = b[:-i]

    return b if len(b) <= maxlen else b[:maxlen]

def find_decimals1(num):

    err = lambda x: x-np.round(x)
    e = 0
    v = num
    while err(v) != 0:
        e += 1
        #print(e)
        #print(num)
        v = num * 10**e
        #print(v)
        #print(err(v))

    if err(v) < 0:
        e += 1

    return e


def find_max_num_decimals(values):
    """
    Find the maximum number of decimals for an iterable of values
    or a single value. The decimal point is included in the return value.
    """

    maxnum = 0
    if isiterable(values):
        for v in values:
            b = find_decimals(v)
            maxnum = max([maxnum, len(b)+1])
    else:
        b = find_decimals(values)
        maxnum = maxnum

    return maxnum

def str_to_bool(string):
    """
    Convert string to bool.
    Not case sensitive.
    """
    if string.lower().strip() == "true":
        return True
    elif string.lower().strip() == "false":
        return False
    else:
        raise Exception("Cannot convert '{}' to bool.".format(string))

def get_cmd_args(argv):
    """
    Take the `argv` arguments apart and split up in arguments and options.
    Options start with `-` and can be stacked. Options starting with `--` cannot 
    be stacked.
    """

    args = []
    options = []
    
    i = 1
    while (i < len(argv)):
        if argv[i].strip()[0] == '-':
            # it's an option
            if argv[i].strip()[1] == '-':
                options.append(argv[i].strip()[2:])
            else:
                for a in argv[i].strip()[1:]:
                    options.append(a)
        else:
            # it's an argument
            args.append(argv[i])
    
    return args, options