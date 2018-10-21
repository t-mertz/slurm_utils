import math # ceil, log10
import sys

import numpy as np  # prod

from ...slurm_interface import api as slurm
from ...slurm_interface import resources

if sys.version.startswith('2'):
    input = raw_input   # compatibility with Python2

def submit(filename, firstmatch=False):
    hwdata = slurm.sinfo_detail()

    # get requested cores and nodes from bash script
    requested_resources = read_sbatch_file(filename)

    idle_resources = []
    queued_resources = []

    if requested_resources[0].nodes() is not None:
        # queue user if this was intentional
        pass

    for cur_resource in requested_resources:
        idle_resources.append(find_optimal_resources(hwdata, cur_resource, idle=True))

        queued_resources.append(find_optimal_resources(hwdata, cur_resource, idle=False))
        # if opt is None:
        #     print("Error: Number of requested cores exceeds total number of "\
        #             +"partition {}. \nAborting.".format(partition))
    

    opt_resource = None
    found = [res in idle_resources for res in requested_resources]
    if np.prod(found):
        opt_resource = requested_resources[found.index(True)]
    else:
        txt = get_resource_summary(idle_resources, queued_resources)
        print(txt, end='')
        selection_query = 'Select an option: '
        error_msg = 'Please provide a number between {} and {}.'.format(
            1, len(txt)
        )
        success = False
        while not success:
            try:
                ind = int(input(selection_query))
                success = True
            except ValueError:
                print(error_msg)

        if ind < len(idle_resources):
            opt_resource = ind - 1
        else:
            opt_resource = ind - len(idle_resources) - 1
    
    # write new numbers to script file
    # submit the job

def find_optimal_resources(hwdata, requested_resource, idle=True):
    # filter partition
    part_hwdata = hwdata.filter_partition(requested_resource.partition())

    # get optimal resource allocation (just idle)
    opt = resources.find_resources(part_hwdata, requested_resource.cpus(), idle=idle)

    return resources.Resource(
        requested_resource.partition(),
        opt[0],
        opt[1]
    )

def read_sbatch_file(filename):
    nodes = None
    ncpus = None
    partitions = None

    with open(filename, 'r') as infile:
        for line in infile:
            if line.strip().startswith('#SBATCH'):
                if 'nodes' in line:
                    nodes = int(line.split('=')[1])
                elif 'ncpus' in line:
                    ncpus = int(line.split('=')[1])
                elif 'partition' in line:
                    partitions = line.split('=')[1].split(',')

    return [resources.Resource(p, ncpus, nodes) for p in partitions]

def get_resource_summary(idle, queued):
    output_txt = []
    total = len(idle) + len(queued)
    max_decimals = math.ceil(math.log10(total+1))
    format_str = "({index:{decimals}d}) partition: {partition:>15s}, CPUs: {cpus:4d}, nodes: {nodes:2d}, ({status})\n"
    ind = 1
    for res in idle:
        output_txt.append(
            format_str.format(
                index=ind,
                decimals=max_decimals,
                partition=res.partition(),
                cpus=res.cpus(),
                nodes=res.nodes(),
                status='idle'
        ))
        ind += 1
    for res in queued:
        output_txt.append(
            format_str.format(
                index=ind,
                decimals=max_decimals,
                partition=res.partition(),
                cpus=res.cpus(),
                nodes=res.nodes(),
                status='pending'
        ))
        ind += 1
    return output_txt