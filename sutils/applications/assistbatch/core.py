from __future__ import print_function
import math # ceil, log10
import sys

import numpy as np  # prod

from ...slurm_interface import api as slurm
from ...slurm_interface import resources

if sys.version.startswith('2'):
    input = raw_input   # compatibility with Python2

def submit(filename, firstmatch=False):
    # get requested cores and nodes from bash script
    requested_resources = read_sbatch_file(filename)

    hwdata = slurm.sinfo_detail()

    idle_resources = []
    queued_resources = []

    if requested_resources[0].nodes() is not None:
        # query user if this was intentional
        pass

    for cur_resource in requested_resources:
        idle_resources.extend(find_optimal_resources(hwdata, cur_resource, idle=True))

        queued_resources.extend(find_optimal_resources(hwdata, cur_resource, idle=False))
        # if opt is None:
        #     print("Error: Number of requested cores exceeds total number of "\
        #             +"partition {}. \nAborting.".format(partition))
    

    found = [res in idle_resources for res in requested_resources]
    if np.prod(found) and len(found) > 1:
        opt_resource = requested_resources[found.index(True)]
    else:
        for rres in queued_resources:
            if rres in idle_resources:
                queued_resources.remove(rres)   # remove duplicates, prefer idle
        summary_txt = get_resource_summary(idle_resources, queued_resources)
        opt_resource = get_option_from_user(summary_txt, idle_resources, queued_resources)
    
    # write new numbers to script file
    write_sbatch_file(filename, opt_resource)

    # submit the job
    res = slurm.sbatch('.', 'asbatch_'+filename)
    print(res.stdout())

def get_option_from_user(txt, idle_resources, queued_resources):
    for line in txt:
        print(line, end='')
    selection_query = 'Select an option: '
    error_msg = 'Please provide a number between {} and {}.'.format(
        1, len(txt)
    )
    success = False
    while not success:
        try:
            ind = int(input(selection_query))
            if len(txt) >= ind > 0:
                success = True
            else:
                raise ValueError(ind, len(txt))
        except ValueError:
            print(error_msg)

    if ind <= len(idle_resources):
        opt_resource = idle_resources[ind - 1]
    else:
        opt_resource = queued_resources[ind - len(idle_resources) - 1]

    return opt_resource

def find_optimal_resources(hwdata, requested_resource, idle=True):
    # filter partition
    part_hwdata = hwdata.filter_partition([requested_resource.partition()])

    # get optimal resource allocation (just idle)
    opt = resources.find_resources(part_hwdata, requested_resource.cpus(), idle=idle)

    if opt is None:
        return []
    else:
        return [resources.Resource(
            requested_resource.partition(),
            opt[0],
            opt[1],
            requested_resource.memory()
        )]

def read_sbatch_file(filename):
    nodes = None
    ntasks = None
    partitions = None
    mem = None

    with open(filename, 'r') as infile:
        for line in infile:
            if line.strip().startswith('#SBATCH'):
                if 'nodes' in line:
                    nodes = int(line.split('=')[1])
                elif 'ntasks' in line:
                    ntasks = int(line.split('=')[1])
                elif 'partition' in line:
                    partitions = line.split('=')[1].strip().split(',')
                elif 'mem=' in line:
                    mem = int(line.split('=')[1])

    if partitions is None:
        raise RuntimeError("partition not specified")
    if ntasks is None:
        raise RuntimeError("ntasks not specified")

    return [resources.Resource(p, ntasks, nodes, mem) for p in partitions]

def write_sbatch_file(filename, resource):
    setmap = {'partition': False, 'ntasks': False, 'nodes': False}
    outfilename = 'asbatch_'+filename
    with open(filename, 'r') as infile:
        with open(outfilename, 'w') as outfile:
            for line in infile:
                newline = line
                if 'partition' in line:
                    newline = '#SBATCH --partition={}\n'.format(resource.partition())
                    setmap['partition'] = True
                elif 'ntasks' in line:
                    newline = '#SBATCH --ntasks={}\n'.format(resource.cpus())
                    setmap['ntasks'] = True
                elif 'nodes' in line and resource.nodes() is not None:
                    newline = '#SBATCH --nodes={}\n'.format(resource.nodes())
                    setmap['nodes'] = True
                elif 'mem' in line and resource.memory() is not None:
                    newline = '#SBATCH --mem={}\n'.format(resource.memory())
                if len(line.strip()) > 0 and '#' not in line:
                    # slurm configuration is over
                    for key, val in setmap.items():
                        if not val:
                            if key == 'nodes':
                                outfile.write('#SBATCH --{key}={value}\n'.format(key=key, value=resource.nodes()))
                outfile.write(newline)
                

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

def add_max_resources(idle_res, hwinfo):
    idle_partitions = [r.partition() for r in idle_res]
    max_resources = resources.get_maximal_resources(hwinfo)
    for p in np.unique(hwinfo['partition']):
        if p not in idle_partitions:
            idle_res.append(max_resources[p])

