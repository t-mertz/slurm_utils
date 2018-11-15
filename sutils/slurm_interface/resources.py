import copy

import numpy as np

from . import api

def cpu_count(sinfo_data):
    """Compute the number of cores per node.

    This function is obsolete. Change to compute the number of cores per 
    partition.
    """
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
        cpus = list(hwdata.filter_idle()['idlecpus'])
    else:
        cpus = list(hwdata['allcpus'])
    for i in range(cpus.count(0)):
        cpus.remove(0) # remove nodes with 0 CPUs
    optimum = _subset_internal(cpus, n)

    if not optimum is False: # needed since bool([]) == False
        ret = (sum(optimum), len(optimum))
    else:
        ret = None
    
    return ret

def _subset_internal(cpus, n, _buf=None):
    """Solves a problem similar to SubsetSum:
    
    Given a list 'cpus' of numbers and a number n find the smallest subset
    'C' of 'cpus' such that sum(C) >= n. Here, 'smallest' refers to sum(C)
    and if ambiguous to the size of the subset.

    Returns the subset.

    '_buf' is internal storage. Don't pass anything!
    """
    # here we setup storage for performance reasons
    if _buf is None:
        _buf = {}
    # check if result has already been calculated
    if ((tuple(sorted(cpus)), n)) in _buf:
        return _buf[(tuple(sorted(cpus)), n)]
    s = sum(cpus)

    # base cases
    if n > s:
        return False
    if n == s:
        return cpus
    if n <= 0:
        return []
    
    uniques = set(cpus) # only need to remove each unique number once

    subsets = [copy.copy(cpus) for i in uniques]
    for i,c in enumerate(uniques):
        tmp = copy.copy(cpus)
        tmp.remove(c)
        exclude = _subset_internal(tmp, n, _buf=_buf)
        include = _subset_internal(tmp, n-c, _buf=_buf)
        if exclude: # compute optimal subset if c is excluded
            if sum(exclude) < sum(subsets[i]):
                subsets[i] = exclude
            elif sum(exclude) == sum(subsets[i]) and len(exclude) < len(subsets[i]):
                subsets[i] = exclude    # resolve ambiguity by requiring smallest length

        if include: # compute optimal subset if c is included
            if sum(include)+c < sum(subsets[i]):
                subsets[i] = include + [c]
            elif sum(include)+c == sum(subsets[i]) and len(include)+1 < len(subsets[i]):
                subsets[i] = include + [c]
    
    # determine the optimal solution out of all picks above
    msum = s
    ind = 0
    for i,cset in enumerate(subsets):
        if sum(cset) < msum:
            ind = i
            msum = sum(subsets[ind])
        elif sum(cset) == msum and len(cset) < len(subsets[ind]):
            ind = i
            msum = sum(subsets[ind])


    _buf[(tuple(sorted(cpus)), n)] = subsets[ind]    # store result to buffer
    return subsets[ind]





class Resource(object):
    """Container for collection of CPUs."""
    def __init__(self, partition, cpus, nodes, mem):
        self._cpus = cpus
        self._partition = partition
        self._nodes = nodes
        self._mem = mem

    def partition(self):
        return self._partition
    
    def cpus(self):
        return self._cpus
    
    def nodes(self):
        return self._nodes

    def memory(self):
        return self._mem
    
    def __eq__(self, obj):
        if isinstance(obj, Resource):
            cond1 = self._cpus == obj._cpus
            cond2 = self._partition == obj._partition
            cond3 = self._nodes == obj._nodes
            cond4 = self._mem == obj._mem
            return cond1 and cond2 and cond3 and cond4
        else:
            False

    def __repr__(self):
        format_str = "<Resource object, partition={partition}, cpus={cpus}, nodes={nodes}, mem={mem}>"
        return format_str.format(
            partition=self._partition,
            cpus=self._cpus,
            nodes=self._nodes,
            mem=self._mem,
        )

    def to_dict(self):
        return {
            'partition' : self._partition,
            'ntasks'    : self._cpus,
            'nodes'     : self._nodes,
            'mem'       : self._mem,
        }

def get_maximal_resources(hwinfo):
    partitions = np.unique(hwinfo['partition'])
    ncpus = []
    nnodes = []
    for p in partitions:
        tmp = hwinfo.filter_partition([p])
        ncpus.append(tmp['allcpus'].sum())
        nnodes.append(len(tmp['allcpus']))

    return {p: Resource(partitions[i], ncpus[i], nnodes[i], None) for i,p in enumerate(partitions)}
    
