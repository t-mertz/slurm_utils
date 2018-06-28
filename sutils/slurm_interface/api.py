# implements an API for SLURM through subprocess

import os
import getpass
import subprocess

def run_command(cmd, args):
    p = subprocess.Popen(args, executable=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    p.terminate()

    retval = 1 if len(stderr) > 0 else 0

    return retval, stdout, stderr

def sbatch(args):
    retval, stdout, stderr = run_command('sbatch', args)
    return retval, stdout

def scancel(args):
    retval, stdout, stderr = run_command('scancel', args)
    return retval, stdout

def squeue(args):
    """Call squeue once to check for jobs of the current user.
    
    Returns an SqueueResult object containing the job data.
    """
    args.append('--noheader')   # this is to make parsing easier
    args.append('--user', getpass.getuser())

    retval, stdout, stderr = run_command('squeue', args)

    lines = stdout.split('\n')
    data = [line.split() for line in lines]
    return retval, SqueueResult(data)


class Result(object):
    pass

class SqueueResult(Result):
    def __init__(self, data):
        self.jobid = [int(d[0]) for d in data]
        self.status = [d[1] for d in data]

    def get(self, jobid):
        try:
            index = self.jobid.find(jobid)
        except ValueError:
            # not in list
            pass
        return {'status': self.status[index]}
