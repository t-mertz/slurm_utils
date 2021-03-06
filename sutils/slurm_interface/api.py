# implements an API for SLURM through subprocess

import os
import getpass
import subprocess
import copy

import numpy as np

from . import config
from ..test import test
from ..utils.util import to_list, stringify_list, make_float

SINFO_DETAIL_FORMAT = "nodehost:.30,"\
                    + "partitionname:.20,"\
                    + "cpusload:.10,"\
                    + "cpusstate:.16,"\
                    + "socketcorethread:.12,"\
                    + "statelong:.14,"\
                    + "memory:.14,"\
                    + "freemem:.14,"\
                    + "allocmem:.14,"\
                    + "features:.50"

SQUEUE_FORMAT = "jobid:.8,"\
              + "partition:.20,"\
              + "name:.30,"\
              + "username:.20,"\
              + "state:.15,"\
              + "timeused:.12,"\
              + "numnodes:.5,"\
              + "nodelist:.30"


def run_command(cmd, args):
    sargs = stringify_list(args)
    if False:#test.testmode():
        test.cmd_buffer.write(cmd + " " + " ".join(args))
        stdout = ""
        stderr = ""
    else:
        p = subprocess.Popen([cmd] + sargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #p.wait()
        stdout, stderr = p.communicate()
        #p.terminate()

    retval = 0 if len(stderr) == 0 else 1

    return retval, stdout.decode('utf-8'), stderr.decode('utf-8')


def _sbatch(script, cpus_per_task=None, mem=None, nodes=None, ntasks=None,
            partition=None, work_dir=None, exclusive=None, test_only=None,
            ignore_error=False):
    argdict = locals()
    argdict.pop('script')
    argdict.pop('ignore_error')
    args = config.SbatchConfig(**argdict).to_list()
    args.append(script)

    retval, stdout, stderr = run_command('sbatch', args)

    if retval != 0 and not ignore_error:
        raise RuntimeError("Call to `sbatch` failed: \n" + stderr)

    if ignore_error:
        stdout += stderr

    return stdout

#def sbatch(work_dir, *args, **kwargs):
def sbatch(script, cpus_per_task=None, mem=None, nodes=None, ntasks=None,
           partition=None, work_dir=None, exclusive=None, test_only=None,
           ignore_error=False):
    #named_args = config.SbatchConfig(work_dir=work_dir).to_list()
    #named_args += args # this is to support extra arguments. No guarantee!
    #for arg in kwargs:
    #    named_args.append("--{}={}".format(arg, kwargs[arg]))

    #retval, stdout, stderr = run_command('sbatch', named_args)
    
    #if retval != 0:
    #    raise RuntimeError("Call to `sbatch` failed: \n" + stderr)
    stdout = _sbatch(script, cpus_per_task=cpus_per_task, mem=mem,
                     nodes=nodes, ntasks=ntasks, partition=partition,
                     work_dir=work_dir, exclusive=exclusive, test_only=test_only,
                     ignore_error=ignore_error)

    return SbatchResult(stdout)

def scancel(job_id):
    #args = config.Scancel_Options(job_id=job_id).to_list()
    args = to_list(job_id)
    retval, stdout, stderr = run_command('scancel', args)
    return 0

def _squeue(args):
    retval, stdout, stderr = run_command('squeue', args)

    if retval != 0:
        raise RuntimeError("Call to `squeue` failed: \n" + stderr)

    return stdout

def squeue(args):
    """Call squeue with given arguments."""
    res = _squeue(args)

    return SqueueResult(res)

def squeue_user():
    """Call squeue once to check for jobs of the current user.
    
    Returns an SqueueResult object containing the job data.
    """
    #args.append('--noheader')   # this is to make parsing easier
    #args.append('--user', getpass.getuser())
    args = config.Squeue_Options(userid=getpass.getuser(), noheader=True).to_list()

    return squeue(args)



def _sinfo(format=None, node=False, noheader=False):
    """Run sinfo and return stdout text."""
    args = config.SinfoConfig(format=format, node=node, noheader=noheader).to_list()

    retval, stdout, stderr = run_command('sinfo', args)

    if retval != 0:
        raise RuntimeError("Call to `sinfo` failed: \n" + stderr)
    
    return stdout

def sinfo(format=None, node=False, noheader=False):
    """Run sinfo and return processed output."""
    stdout = _sinfo(format=format, node=node, noheader=noheader)
    
    return SinfoResult(stdout)


def sinfo_detail():
    """Run sinfo with a predefined format specification that generates 
    detailed information about the node hardware.
    """
    return SinfoData(sinfo(format=SINFO_DETAIL_FORMAT, node=True, noheader=True))

class Result(object):
    def __init__(self, data):
        self._data = data.strip().split('\n')
        # remove empty lines
        self._data = [l for l in self._data if len(l) > 0]
    
    def __len__(self):
        return len(self._data)

class SbatchResult(Result):
    def stdout(self):
        return self._data[0]

class SqueueResult(Result):
    def __init__(self, data):
        # convert to numpy array and use slices?

        tmp_data = [line.split() for line in data.split('\n')]
        if len(tmp_data[-1]) == 0:
            del tmp_data[-1]
        self._data = np.array(tmp_data)
        self._njobs = len(tmp_data)
        if self._njobs > 0:
            self.jobid = [int(d) for d in self._data[:, 0]]
            self.status = [d for d in self._data[:, 4]]
        else:
            self.jobid = []
            self.status = []

    def get(self, jobid):
        try:
            index = self.jobid.index(jobid)
        except ValueError:
            # not in list
            pass
        return {'status': self.status[index]}

    def get_ids(self):
        return self.jobid

    def __iter__(self):
        for i in self.jobid:
            yield i

    def __eq__(self, obj):
        return np.all(self._data == obj._data)

class SinfoResult(Result):
    def __init__(self, data):
        super(SinfoResult, self).__init__(data)

        data_table = [[entry.strip() for entry in line.split()] for line in self._data]
        if len(self._data) == 0:
            data_table = [[]]
        self._data_array = np.array(data_table)

    def __iter__(self):
        for i in range(len(self)):
            yield self._data_array[i, :]

class SinfoData(object):
    def __init__(self, *args):
        if len(args) == 0:
            info = {}
            info['nodehost'] = np.array([], dtype=np.unicode_)
            info['partition'] = np.array([], dtype=np.unicode_)
            info['cpusload'] = np.array([], dtype=float)
            info['alloccpus'] = np.array([], dtype=int)
            info['idlecpus'] = np.array([], dtype=int)
            info['othercpus'] = np.array([], dtype=int)
            info['allcpus'] = np.array([], dtype=int)
            info['sockets_per_node'] = np.array([], dtype=int)
            info['cores_per_socket'] = np.array([], dtype=int)
            info['threads_per_core'] = np.array([], dtype=int)
            info['state'] = np.array([], dtype=np.unicode_)
            info['memory'] = np.array([], dtype=int)
            info['freememory'] = np.array([], dtype=int)
            info['allocmemory'] = np.array([], dtype=int)
            info['features'] = np.array([], dtype=np.unicode_)
            self._info_data = info
        elif len(args) == 1:
            if isinstance(args[0], SinfoResult):
                self._init_from_result(args[0])
            elif isinstance(args[0], SinfoData):
                self._init_from_sinfodata(args[0])
            elif isinstance(args[0], str):
                self._init_from_string(args[0])
            else:
                TypeError("Cannot initialize from type '%s'" % str(type(args[0])))
        else:
            raise TypeError("__init__() takes up to 1 positional arguments but %d was given" % len(args))

    def _init_from_sinfodata(self, obj):
        """Copy construction."""
        self._info_data = copy.deepcopy(obj._info_data)
    
    def _init_from_string(self, obj):
        """Construct from output string of sinfo."""
        self._init_from_result(SinfoResult(obj))

    def _init_from_result(self, res):
        info = {}
        if len(res) == 0:
            info['nodehost'] = np.array([], dtype=np.unicode_)
            info['partition'] = np.array([], dtype=np.unicode_)
            info['cpusload'] = np.array([], dtype=float)
            info['alloccpus'] = np.array([], dtype=int)
            info['idlecpus'] = np.array([], dtype=int)
            info['othercpus'] = np.array([], dtype=int)
            info['allcpus'] = np.array([], dtype=int)
            info['sockets_per_node'] = np.array([], dtype=int)
            info['cores_per_socket'] = np.array([], dtype=int)
            info['threads_per_core'] = np.array([], dtype=int)
            info['state'] = np.array([], dtype=np.unicode_)
            info['memory'] = np.array([], dtype=int)
            info['freememory'] = np.array([], dtype=int)
            info['allocmemory'] = np.array([], dtype=int)
            info['features'] = np.array([], dtype=np.unicode_)
        else:
            info['nodehost'] = np.copy(res._data_array[:, 0]).astype(np.unicode_)
            info['partition'] = np.copy(res._data_array[:, 1]).astype(np.unicode_)
            #try:
            #    info['cpusload'] = np.copy(res._data_array[:, 2]).astype(float)
            #except ValueError:
            #    inds = is_float(res._data_array[:, 2])
            #    tmp = np.copy(res._data_array[:, 2])
            #    tmp[np.logical_not(inds)] = 0.0
            #    info['cpusload'] = tmp.astype(float)
            info['cpusload'] = make_float(np.copy(res._data_array[:, 2])).astype(float)

            tmp = np.array([s.split('/') for s in res._data_array[:, 3]], dtype=int)
            info['alloccpus'] = tmp[:, 0]
            info['idlecpus'] = tmp[:, 1]
            info['othercpus'] = tmp[:, 2]
            info['allcpus'] = tmp[:, 3]

            tmp = np.array([s.split(':') for s in res._data_array[:, 4]], dtype=int)
            info['sockets_per_node'] = tmp[:, 0]
            info['cores_per_socket'] = tmp[:, 1]
            info['threads_per_core'] = tmp[:, 2]

            info['state'] = np.copy(res._data_array[:, 5]).astype(np.unicode_)
            info['memory'] = make_float(np.copy(res._data_array[:, 6])).astype(int)
            info['freememory'] = make_float(np.copy(res._data_array[:, 7])).astype(int)
            info['allocmemory'] = make_float(np.copy(res._data_array[:, 8])).astype(int)

            info['features'] = np.copy(res._data_array[:, 9]).astype(np.unicode_)
        
        self._info_data = info

    def __getitem__(self, key):
        return self._info_data[key]
    
    def __contains__(self, key):
        return key in self._info_data
    
    def filter_partition(self, partitions):
        """Create a new instance containing only the specified partitions."""
        inst = SinfoData()

        inds = []
        for p in partitions:
            inds.append(np.argwhere(self._info_data['partition']==p).flatten())
        inds = np.sort(np.concatenate(inds))

        inst._info_data['nodehost'] = self._info_data['nodehost'][inds]
        inst._info_data['partition'] = self._info_data['partition'][inds]
        inst._info_data['cpusload'] = self._info_data['cpusload'][inds]
        inst._info_data['alloccpus'] = self._info_data['alloccpus'][inds]
        inst._info_data['idlecpus'] = self._info_data['idlecpus'][inds]
        inst._info_data['othercpus'] = self._info_data['othercpus'][inds]
        inst._info_data['allcpus'] = self._info_data['allcpus'][inds]
        inst._info_data['sockets_per_node'] = self._info_data['sockets_per_node'][inds]
        inst._info_data['cores_per_socket'] = self._info_data['cores_per_socket'][inds]
        inst._info_data['threads_per_core'] = self._info_data['threads_per_core'][inds]
        inst._info_data['state'] = self._info_data['state'][inds]
        inst._info_data['memory'] = self._info_data['memory'][inds]
        inst._info_data['freememory'] = self._info_data['freememory'][inds]
        inst._info_data['allocmemory'] = self._info_data['allocmemory'][inds]
        inst._info_data['features'] = self._info_data['features'][inds]
        
        return inst

    def _copy_info_data(self, inst, inds=slice(None)):
        inst._info_data['nodehost'] = self._info_data['nodehost'][inds]
        inst._info_data['partition'] = self._info_data['partition'][inds]
        inst._info_data['cpusload'] = self._info_data['cpusload'][inds]
        inst._info_data['alloccpus'] = self._info_data['alloccpus'][inds]
        inst._info_data['idlecpus'] = self._info_data['idlecpus'][inds]
        inst._info_data['othercpus'] = self._info_data['othercpus'][inds]
        inst._info_data['allcpus'] = self._info_data['allcpus'][inds]
        inst._info_data['sockets_per_node'] = self._info_data['sockets_per_node'][inds]
        inst._info_data['cores_per_socket'] = self._info_data['cores_per_socket'][inds]
        inst._info_data['threads_per_core'] = self._info_data['threads_per_core'][inds]
        inst._info_data['state'] = self._info_data['state'][inds]
        inst._info_data['memory'] = self._info_data['memory'][inds]
        inst._info_data['freememory'] = self._info_data['freememory'][inds]
        inst._info_data['allocmemory'] = self._info_data['allocmemory'][inds]
        inst._info_data['features'] = self._info_data['features'][inds]

    def filter_cpus(self, n):
        """Create a new instance containing only nodes with at least n cpus."""
        inst = SinfoData()
        inds = np.argwhere(self._info_data['allcpus'] >= n).flatten()
        self._copy_info_data(inst, inds=inds)

        return inst
        
    def filter_memory(self, m):
        """Create a new instance containing only nodes with at least m MB of memory."""
        inst = SinfoData()
        inds = np.argwhere(self._info_data['memory'] >= m).flatten()
        self._copy_info_data(inst, inds=inds)

        return inst
    
    def filter_mem_per_cpu(self, m):
        """Create a new instance containing only nodes with at least m MB of memory per CPU."""
        inst = SinfoData()
        inds = np.argwhere(self._info_data['memory'] / self._info_data['allcpus'] >= m).flatten()
        self._copy_info_data(inst, inds=inds)

        return inst

    def filter_idle(self):
        """Create a new instance containing only idle nodes."""
        inst = SinfoData()
        inds = np.argwhere(
            np.logical_and(
                self._info_data['idlecpus'] == self._info_data['allcpus'],
                self._info_data['state'] == 'idle'
                )
        ).flatten()
        self._copy_info_data(inst, inds=inds)

        return inst
    
    def mem_per_cpu(self):
        return self._info_data['memory'] / self._info_data['allcpus']

    def freemem_per_idlecpu(self):
        return self._info_data['freememory'] / self._info_data['idlecpus']

    def __eq__(self, obj):
        res = True
        for key, val in self._info_data.items():
            res *= np.all(obj[key] == val)
        return res
