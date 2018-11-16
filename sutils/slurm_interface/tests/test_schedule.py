import unittest
from unittest.mock import Mock, patch
import datetime

from .. import schedule
from .. import api as slurm

class TestGetScheduledStart(unittest.TestCase):
    def setUp(self):
        self.stdout = "sbatch: Job 417957 to start at 2018-11-22T17:14:32 using 48 processors on dfg-xeon[02,15-16]"
        self.sbatch_res = slurm.SbatchResult(self.stdout)

    @patch("sutils.slurm_interface.api.sbatch")
    def test_calls_sbatch_with_test_only(self, mock_sbatch):
        mock_sbatch.return_value = self.sbatch_res
        script = "scriptname"
        kwargs = {
            'keyword': 'argument',
            'list': '.'
        }
        schedule.get_scheduled_start(script, kwargs)
        kwargs['test_only'] = True
        mock_sbatch.assert_called_once_with(script, **kwargs)

    @patch("sutils.slurm_interface.api.sbatch")
    def test_does_not_change_kwargs(self, mock_sbatch):
        mock_sbatch.return_value = self.sbatch_res
        script = "scriptname"
        kwargs = {
            'keyword': 'argument',
            'list': '.'
        }
        schedule.get_scheduled_start(script, kwargs)
        self.assertEqual(kwargs, {'keyword': 'argument', 'list': '.'})

    @patch("sutils.slurm_interface.api.sbatch")
    def test_returns_time(self, mock_sbatch):
        mock_sbatch.return_value = self.sbatch_res
        self.assertEqual(schedule.get_scheduled_start("", {}),
            datetime.datetime(2018, 11, 22, 17, 14, 32))


class TestGetScheduledWaitingTime(unittest.TestCase):
    def setUp(self):
        self.stdout = "sbatch: Job 417957 to start at 2018-11-22T17:14:32 using 48 processors on dfg-xeon[02,15-16]"
        self.sbatch_res = slurm.SbatchResult(self.stdout)

    @patch("sutils.slurm_interface.api.sbatch")
    @patch("sutils.slurm_interface.schedule.get_datetime_now")
    def test_returns_timedelta(self, mock_now, mock_sbatch):
        mock_sbatch.return_value = self.sbatch_res
        current_time = datetime.datetime(2018, 11, 20, 15, 0, 0)
        mock_now.return_value = current_time
        self.assertEqual(schedule.get_scheduled_waiting_time("", {}),
            datetime.timedelta(2, 8072))

    @patch("sutils.slurm_interface.api.sbatch")
    @patch("sutils.slurm_interface.schedule.get_datetime_now")
    def test_calls_get_datetime_now(self, mock_now, mock_sbatch):
        mock_sbatch.return_value = self.sbatch_res
        current_time = datetime.datetime(2018, 11, 20, 15, 0, 0)
        mock_now.return_value = current_time
        schedule.get_scheduled_waiting_time("", {})
        mock_now.assert_called_once_with()
