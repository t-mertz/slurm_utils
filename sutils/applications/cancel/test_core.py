import unittest
from unittest.mock import Mock, patch, MagicMock

from . import core


class TestGetJobs(unittest.TestCase):
    @patch("sutils.applications.cancel.core.slurm.squeue_user", Mock())
    def test_calls_squeue_user(self):
        squeue_stdout = "123456  partition1  jobname1   username1  PENDING  0:00  2  (Priority)\n"\
                     + "123457  partition2  jobname2   username2  RUNNING  1-01:41:13  4  partition1node[01-04]\n"
        mock_squeue = core.slurm.squeue_user
        mock_squeue.return_value = core.slurm.SqueueResult(squeue_stdout)
        core.get_jobs()

        mock_squeue.assert_called_once_with()

    @patch("sutils.applications.cancel.core.slurm.squeue_user", Mock())
    def test_returns_joblist(self):
        squeue_stdout = "123456  partition1  jobname1   username1  PENDING  0:00  2  (Priority)\n"\
                     + "123457  partition2  jobname2   username2  RUNNING  1-01:41:13  4  partition1node[01-04]\n"
        mock_squeue = core.slurm.squeue_user
        mock_squeue.return_value = core.slurm.SqueueResult(squeue_stdout)
        jobs = core.get_jobs()

        self.assertEqual(jobs, [123456, 123457])

    @patch("sutils.applications.cancel.core.slurm.squeue_user", Mock())
    def test_returns_joblist_sorted(self):
        squeue_stdout = "123466  partition1  jobname1   username1  PENDING  0:00  2  (Priority)\n"\
                     + "123457  partition2  jobname2   username2  RUNNING  1-01:41:13  4  partition1node[01-04]\n"
        mock_squeue = core.slurm.squeue_user
        mock_squeue.return_value = core.slurm.SqueueResult(squeue_stdout)
        jobs = core.get_jobs()

        self.assertEqual(jobs, [123457, 123466])
