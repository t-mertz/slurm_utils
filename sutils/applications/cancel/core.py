from ...slurm_interface import api as slurm
import sys

def get_jobs():
    """Returns a sorted list of queued or running jobs belonging to the current
    user.
    """
    retval, res = slurm.squeue_user()
    joblist = res.get_ids()
    return sorted(joblist)

def cancel_last(N):
    """Cancel the last N queued or running jobs of the current user."""
    joblist = get_jobs()[::-1]
    max_index = min(len(joblist), N)
    cancel_list(joblist[:max_index])

def cancel_first(N):
    """Cancel the first N queued or running jobs of the current user."""
    joblist = get_jobs()
    max_index = min(len(joblist), N)
    cancel_list(joblist[:max_index])

def cancel_all():
    """Cancel all queued or running jobs of the current user."""
    joblist = get_jobs()
    cancel_list(joblist)

def cancel_list(job_list):
    """Cancel jobs of the current user."""
    N = len(job_list)
    for i, jobid in enumerate(job_list):
        sys.stdout.write("{}/{}: Cancelling {} ...".format(i+1, N, jobid))
        slurm.scancel(job_id=jobid)
        sys.stdout.write(" done\n")

def cancel_job(job_id):
    """Cancel a single job of the current user."""
    slurm.scancel(job_id=int(job_id))
