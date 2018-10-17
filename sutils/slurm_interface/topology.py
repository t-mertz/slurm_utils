import numpy as np

from . import api

def cpu_count():
    res = api.sinfo()
    
    count = {}

    for node in res:
        node_name = node[1]
        ncpus = int(node[3].split('/')[-1])
        count.setdefault(node_name, 0)
        count[node_name] += ncpus
    
    return count
