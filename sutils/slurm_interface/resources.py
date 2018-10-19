import copy

import numpy as np

from . import api

def cpu_count(sinfo_data):    
    count = {}

    for i,node_name in enumerate(sinfo_data['nodehost']):
        ncpus = sinfo_data['allcpus'][i]
        count.setdefault(node_name, 0)
        count[node_name] += ncpus
    
    return count

def is_cpu_commensurate(sinfo_data, n, status='all'):
    """Check if an allocation of n is commensurate with the hardware."""
    assert status in ['all', 'idle', 'other', 'alloc'], "Invalid status: %s" % status
    key = status + 'cpus'
    counts = np.unique(sinfo_data[key])
    cond1 = 0 in n % counts

    #fits = np.argwhere(n % sinfo_data[key] == 0)
    return cond1
    

def find_resources(hwdata, n, idle=False):
    """Find resources for an allocation of n CPUs.
    
    Returns number of CPUs and the number of nodes.
    """
    if idle:
        key = 'idlecpus'
    else:
        key = 'allcpus'
    cpus = list(hwdata[key])
    optimum = _subset_internal(cpus, n)

    return sum(optimum), len(optimum)

def _subset_internal(cpus, n, buf=None):
    if buf is None:
        buf = {}
    if ((tuple(sorted(cpus)), n)) in buf:
        return buf[(tuple(sorted(cpus)), n)]
    s = sum(cpus)

    if n > s:
        return False
    if n == s:
        return cpus
    if n <= 0:
        return []
    
    uniques = set(cpus)

    subsets = [copy.copy(cpus) for i in uniques]
    for i,c in enumerate(uniques):
        tmp = copy.copy(cpus)
        tmp.remove(c)
        exclude = _subset_internal(tmp, n, buf=buf)
        include = _subset_internal(tmp, n-c, buf=buf)
        if exclude:
            if sum(exclude) < sum(subsets[i]):
                subsets[i] = exclude
            elif sum(exclude) == sum(subsets[i]) and len(exclude) < len(subsets[i]):
                subsets[i] = exclude

        if include:
            if sum(include)+c < sum(subsets[i]):
                subsets[i] = include + [c]
            elif sum(include)+c == sum(subsets[i]) and len(include)+1 < len(subsets[i]):
                subsets[i] = exclude
    
    msum = s
    ind = 0
    for i,cset in enumerate(subsets):
        if sum(cset) < msum:
            ind = i
            msum = sum(subsets[ind])
        elif sum(cset) == msum and len(cset) < len(subsets[ind]):
            ind = i
            msum = sum(subsets[ind])


    buf[(tuple(sorted(cpus)), n)] = subsets[ind]
    return subsets[ind]





class Resource(object):
    """Container for collection of CPUs."""
    def __init__(self, cpus):
        if len(cpus) == 0 or 0 in cpus:
            raise ValueError("Empty resource is invalid.")
        self._cpus = cpus

    def __len__(self):
        return len(self._cpus)

    def __eq__(self, obj):
        if isinstance(obj, Resource):
            return self._cpus == obj._cpus
        else:
            False
