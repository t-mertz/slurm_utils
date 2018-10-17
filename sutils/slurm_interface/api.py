# implements an API for SLURM through subprocess

import os
import getpass
import subprocess

import numpy as np

from . import config
from ..test import test
from ..utils.util import to_list

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
    args = config.SinfoConfig(format=format, node=node, noheader=noheader).to_list()

    retval, stdout, stderr = run_command('sinfo', args)

    if retval != 0:
        raise RuntimeError("Call to `sinfo` failed: \n" + stderr)
    
    return stdout

def sinfo(format=None, node=False, noheader=False):
    stdout = _sinfo(format=format, node=node, noheader=noheader)
    
    return SinfoResult(stdout)

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
