# implements an API for SLURM through subprocess

import os
import getpass
import subprocess

import numpy as np

from . import config
from ..test import test
from ..utils.util import to_list

SINFO_DETAIL_FORMAT = "'nodehost:.10',"\
                    + "'partitionname:.10',"\
                    + "'cpusload:.10',"\
                    + "'cpusstate:.14',"\
                    + "'socketcorethread:.8',"\
                    + "'statelong:.12',"\
                    + "'memory:.8',"\
                    + "'freemem:.10',"\
                    + "'allocmem:.10',"\
                    + "'feature:.11'"

def run_command(cmd, args):
    if test.testmode():
        test.cmd_buffer.write(cmd + " " + " ".join(args))
        stdout = ""
        stderr = ""
    else:
        p = subprocess.Popen(args, executable=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        stdout, stderr = p.communicate()
        p.terminate()

    retval = 0 if len(stderr) > 0 else 1

    return retval, stdout, stderr

def sbatch(work_dir, *args, **kwargs):
    named_args = config.SbatchConfig(work_dir=work_dir).to_list()
    named_args += args # this is to support extra arguments. No guarantee!
    for arg in kwargs:
        named_args.append("--{}={}".format(arg, kwargs[arg]))

    retval, stdout, stderr = run_command('sbatch', named_args)
    return retval, stdout

def scancel(job_id):
    #args = config.Scancel_Options(job_id=job_id).to_list()
    args = to_list(job_id)
    retval, stdout, stderr = run_command('scancel', args)
    return 0

def squeue(args):
    retval, stdout, stderr = run_command('squeue', args)
    return retval, stdout

def squeue_user():
    """Call squeue once to check for jobs of the current user.
    
    Returns an SqueueResult object containing the job data.
    """
    #args.append('--noheader')   # this is to make parsing easier
    #args.append('--user', getpass.getuser())
    args = config.Squeue_Options(userid=getpass.getuser(), noheader=True).to_list()

    retval, stdout = squeue(args)

    lines = stdout.split('\n')
    data = [line.split() for line in lines]
    return retval, SqueueResult(data)



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

class SqueueResult(Result):
    def __init__(self, data):
        # convert to numpy array and use slices?
        if len(data[0]) > 0:
            self.jobid = [int(d[0]) for d in data]
            self.status = [d[1] for d in data]
        else:
            self.jobid = None
            self.status = None

    def get(self, jobid):
        try:
            index = self.jobid.find(jobid)
        except ValueError:
            # not in list
            pass
        return {'status': self.status[index]}

    def get_ids(self):
        return self.jobid

    def __iter__(self):
        for i in self.jobid:
            yield i

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
    def __init__(self, res):
        info = {}
        info['nodehost'] = np.copy(res._data_array[:, 0]).astype(np.unicode_)
        info['partition'] = np.copy(res._data_array[:, 1]).astype(np.unicode_)
        info['cpusload'] = np.copy(res._data_array[:, 2]).astype(float)

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
        info['memory'] = np.copy(res._data_array[:, 6]).astype(int)
        info['freememory'] = np.copy(res._data_array[:, 7]).astype(int)
        info['allocmemory'] = np.copy(res._data_array[:, 8]).astype(int)

        info['features'] = np.copy(res._data_array[:, 9]).astype(np.unicode_)

        self._info_data = info

    def __getitem__(self, key):
        return self._info_data[key]
    
    def __contains__(self, key):
        return key in self._info_data
