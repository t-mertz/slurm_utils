# implements an API for SLURM through subprocess

import os
import getpass
import subprocess

from . import config

def run_command(cmd, args):
    p = subprocess.Popen(args, executable=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    p.terminate()

    retval = 0 if len(stderr) > 0 else 1

    return retval, stdout, stderr

def sbatch(work_dir, *args):
    named_args = config.SbatchConfig(work_dir=work_dir).to_list()
    named_args += args # this is to support extra arguments. No guarantee!

    retval, stdout, stderr = run_command('sbatch', named_args)
    return retval, stdout

def scancel(job_id):
    args = config.Scancel_Options(job_id=job_id).to_list()
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


class Result(object):
    pass

class SqueueResult(Result):
    def __init__(self, data):
        # convert to numpy array and use slices?
        self.jobid = [int(d[0]) for d in data]
        self.status = [d[1] for d in data]

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
