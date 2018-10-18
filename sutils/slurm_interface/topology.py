import numpy as np

from . import api

def cpu_count(sinfo_data):    
    count = {}

    for i,node_name in enumerate(sinfo_data['nodehost']):
        ncpus = sinfo_data['allcpus'][i]
        count.setdefault(node_name, 0)
        count[node_name] += ncpus
    
    return count
