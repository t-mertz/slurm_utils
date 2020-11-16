from __future__ import print_function
import math # ceil, log10
import sys

import numpy as np  # prod

from ...slurm_interface import api as slurm
from ...slurm_interface import resources
from ...slurm_interface import config as slurm_config
from ...slurm_interface import schedule
from . import units

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

    max_mem = resources.get_maximal_memory(hwdata)
    max_cpus = None

    for cur_resource in requested_resources:
        req_mem = 0 if cur_resource.memory() is None else cur_resource.memory()
        if req_mem > max_mem[cur_resource.partition()]:
            continue    # skip partition if memory requirement cannot be fulfilled
        idle_resources.extend(find_optimal_resources(hwdata.filter_mem_per_cpu([cur_resource.mem_per_cpu()]),
                                                     cur_resource, idle=True))
        add_max_resources(idle_resources, 
                          hwdata.filter_partition([cur_resource.partition()]).filter_mem_per_cpu([cur_resource.mem_per_cpu()]))

        queued_resources.extend(find_optimal_resources(hwdata.filter_mem_per_cpu([cur_resource.mem_per_cpu()]), 
                                cur_resource, idle=False))
        # if opt is None:
        #     print("Error: Number of requested cores exceeds total number of "\
        #             +"partition {}. \nAborting.".format(partition))


    if len(idle_resources) == 0 and len(queued_resources) == 0:
        sys.stdout.write("Not enough resources available.\n")
        return 1

    found = [res in idle_resources for res in requested_resources]
    if sum(found) and len(found) > 0:
        opt_resource = requested_resources[found.index(True)]
    else:
        for rres in queued_resources:
            if rres in idle_resources:
                queued_resources.remove(rres)   # remove duplicates, prefer idle

        summary_txt = get_resource_summary(idle_resources, queued_resources)
        opt_resource = get_option_from_user(summary_txt, idle_resources, queued_resources)
    
    # write new numbers to script file
    #write_sbatch_file(filename, opt_resource)

    # submit the job
    #res = slurm.sbatch('asbatch_'+filename, **opt_resource.to_dict())
    del opt_resource["memory"]      # don't change what's in the script
    del opt_resource["mem-per-cpu"] #

    try:
        res = slurm.sbatch(filename, exclusive=True, **opt_resource.to_dict())
    except RuntimeError as e:
        print(f"Sbatch error:\n{e}")
        sys.exit(1)
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
    mem_per_cpu = None

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
                    mem = units.convert_to_base(line.split('=')[1])
                elif 'mem-per-cpu' in line:
                    mem_per_cpu = units.convert_to_base(line.split('=')[1])

    if partitions is None:
        raise RuntimeError("partition not specified")
    if ntasks is None:
        raise RuntimeError("ntasks not specified")
    
    if mem_per_cpu is not None:
        mem = mem_per_cpu * ntasks

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
    max_decimals = int(math.ceil(math.log10(total+1)))
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
        # time = schedule.get_scheduled_waiting_time("script.sh", res.to_dict())
        # time = time.total_seconds()
        # time = int(time) if time >= 0 else 0
        # days = time // 86400
        # hours = (time % 86400) // 3600
        # minutes = ((time % 86400) % 3600 ) // 60
        # seconds = ((time % 86400) % 3600 ) % 60
        output_txt.append(
            format_str.format(
                index=ind,
                decimals=max_decimals,
                partition=res.partition(),
                cpus=res.cpus(),
                nodes=res.nodes(),
                #status='allocated'+" "+"{}-{:02d}:{:02d}:{:02d}".format(days, hours, minutes, seconds)
                status='allocated'
        ))
        ind += 1
    return output_txt

def add_max_resources(idle_res, hwinfo):
    hwinfo_idle = hwinfo.filter_idle()
    idle_partitions = [r.partition() for r in idle_res]
    max_resources = resources.get_maximal_resources(hwinfo_idle)
    for p in np.unique(hwinfo_idle['partition']):
        if p not in idle_partitions:# and max_resources[p].cpus() > 0:
            idle_res.append(max_resources[p])

