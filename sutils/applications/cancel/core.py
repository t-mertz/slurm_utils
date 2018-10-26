from ...slurm_interface import api as slurm
#from ...test import test
from ...utils.util import srange
import sys

def get_jobs():
    """Returns a sorted list of queued or running jobs belonging to the current
    user.
    """
    res = slurm.squeue_user()
    #if test.testmode():
    #    return list(srange(3))
    joblist = res.get_ids()
    return sorted(joblist)

def cancel_last(N, force=False):
    """Cancel the last N queued or running jobs of the current user."""
    joblist = get_jobs()[::-1]
    max_index = min(len(joblist), N)
    cancel_list(joblist[:max_index], force=force)

def cancel_first(N, force=False):
    """Cancel the first N queued or running jobs of the current user."""
    joblist = get_jobs()
    max_index = min(len(joblist), N)
    cancel_list(joblist[:max_index], force=force)

def cancel_all(force=False):
    """Cancel all queued or running jobs of the current user."""
    joblist = get_jobs()
    cancel_list(joblist, force=force)

def cancel_list(job_list, force=False):
    """Cancel jobs of the current user."""
    N = len(job_list)
    if not force:
        for i, jobid in enumerate(job_list):
            sys.stdout.write("{}/{}: Cancelling {} ...".format(i+1, N, jobid))
            slurm.scancel(job_id=jobid)
            sys.stdout.write(" done\n")
    else:
        slurm.scancel(job_id=job_list)
        sys.stdout.write("Cancelled {} jobs.\n".format(N))

def cancel_job(job_id):
    """Cancel a single job of the current user."""
    slurm.scancel(job_id=int(job_id))
