import unittest
from unittest.mock import patch

from ...slurm_interface import resources as resources
from ...slurm_interface import api as slurm
from . import core

class TestGetResourceSummary(unittest.TestCase):
    def test_print_none(self):
        idle = []
        queued = []
        self.assertEqual(core.get_resource_summary(idle, queued), [])
        
    def test_print_one_idle(self):
        idle = [resources.Resource('partition', 2, 1)]
        queued = []
        ret = ["(1) partition:       partition, CPUs:    2, nodes:  1, (idle)\n"]
        self.assertEqual(core.get_resource_summary(idle, queued), ret)

    def test_print_one_queued(self):
        idle = []
        queued = [resources.Resource('partition', 2, 1)]
        ret = ["(1) partition:       partition, CPUs:    2, nodes:  1, (pending)\n"]
        self.assertEqual(core.get_resource_summary(idle, queued), ret)

    def test_print_two_idle_queued(self):
        idle = [resources.Resource('partition3', 4, 2),
                resources.Resource('partition4', 1, 2)
               ]
        queued = [resources.Resource('partition', 2, 1),
                  resources.Resource('partition1', 3, 1)
                 ]
        ret = [
            "(1) partition:      partition3, CPUs:    4, nodes:  2, (idle)\n",
            "(2) partition:      partition4, CPUs:    1, nodes:  2, (idle)\n",
            "(3) partition:       partition, CPUs:    2, nodes:  1, (pending)\n",
            "(4) partition:      partition1, CPUs:    3, nodes:  1, (pending)\n"
            ]
        self.assertEqual(core.get_resource_summary(idle, queued), ret)

class TestFindOptimalResources(unittest.TestCase):
    def setUp(self):
        self.sinfo_stdout =  "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        self.infodat = slurm.SinfoData(self.sinfo_stdout)

    @patch("sutils.slurm_interface.api.SinfoData.filter_partition")
    def test_calls_filter_partition(self, filter_partition):
        req = resources.Resource('partition', 1, 1)
        filter_partition.return_value = slurm.SinfoData(self.sinfo_stdout.split('\n')[0])
        core.find_optimal_resources(self.infodat, req, idle=True)

        filter_partition.assert_called_once_with('partition')
    
    @patch("sutils.slurm_interface.resources.find_resources")
    @patch("sutils.slurm_interface.api.SinfoData.filter_partition")
    def test_calls_find_resources(self, filter_partition, find_resources):
        part_infodat = slurm.SinfoData(self.sinfo_stdout.split('\n')[0])
        filter_partition.return_value = part_infodat
        find_resources.return_value = [1, 2]

        req = resources.Resource('partition', 1, 1)
        core.find_optimal_resources(self.infodat, req, idle=True)

        find_resources.assert_called_once_with(part_infodat, 1, idle=True)

    @patch("sutils.slurm_interface.resources.find_resources")
    def test_returns_optimal_resource(self, find_resources):
        find_resources.return_value = (10, 2)
        req = resources.Resource('partition', 1, 1)
        ret = core.find_optimal_resources(self.infodat, req, idle=True)
        opt = resources.Resource('partition', 10, 2)
        self.assertEqual(ret, opt)

class TestReadSbatchFile(unittest.TestCase):
    pass
