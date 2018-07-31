from ...config import iniconfig

import copy

def check_compatibility(file1, file2):
    """Compare two config files for compatibility.
    
    Compatibility is determined by the following indicators:
    - number of parameters
    - names of parameters
    - values of parameters
    """
    pass

def compare_config(config1, config2):
    """Compare two config dicts and return a dict containing the differences."""

    if config1 == config2:
        return dict()

    keys2 = config2.keys()
    visited = dict([[n, dict([[o, False] for o in config2[n].keys()])] for n in keys2]) # groups that haven't been visited will be
                                                # added in the end

    diff = dict()

    # we compare all groups in config1 with those of config2
    for name,group in config1.items():
        if name in config2:
            temp = []   # stores differences for current group
            for option,value in group.items():
                if option in config2[name]:
                    visited[name][option] = True   # mark current group as visited
                    if config2[name][option] != value:
                        temp.append(option)
                else:
                    temp.append(option)

            if len(temp) > 0:
                diff[name] = copy.deepcopy(temp)
        else:
            diff[name] = group

    # finally add all unvisited options from config2
    for name, group in visited.items():
        tmp = []
        for option in group:
            if not group[option]:
                tmp.append(option)
            
        if len(tmp) > 0:
            if name in diff:
                diff[name].append(copy.deepcopy(tmp))
            else:
                diff[name] = copy.deepcopy(tmp)

    return diff

def print_diff(file1, file2):
    """Print the difference between two config files.

    Output is sorted w.r.t. option groups and contains one option per line.
    The first character is the number of the file (1 or 2) from which the option was read.
    """
    config1 = iniconfig.read(file1)
    config2 = iniconfig.read(file2)
    diff = compare_config(config1, config2)

    total = len(diff.keys())

    for i,(name,group) in enumerate(diff.items()):
        print("[{}]".format(name))
        for option in group:
            try:
                print("{ind}:{option}={value}".format(ind=1, option=option, value=config1[name][option]))
            except KeyError:
                print("{ind}:{option}=".format(ind=1, option=option))
            try:
                print("{ind}:{option}={value}".format(ind=2, option=option, value=config2[name][option]))
            except KeyError:
                print("{ind}:{option}=".format(ind=2, option=option))
        
        if i < total-1:
            print("") # newline for aesthetics
