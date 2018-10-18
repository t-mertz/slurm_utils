import unittest
from unittest.mock import Mock, patch

from .. import topology
from .. import api as slurm

class TestCpuCount(unittest.TestCase):
    def test_none(self):
        retval = ""
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {}
        self.assertEqual(topology.cpu_count(data), count)
        
    def test_empty_lines_are_deleted(self):
        retval = "\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {}
        self.assertEqual(topology.cpu_count(data), count)
    
    def test_single_node(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {"node01": 4}
        self.assertEqual(topology.cpu_count(data), count)
        
    def test_two_nodes(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {"node01": 4, "node02": 4}
        self.assertEqual(topology.cpu_count(data), count)
        