import unittest
from unittest.mock import Mock, patch

from .. import topology
from .. import api as slurm

@patch("sutils.slurm_interface.api._sinfo")
class TestCpuCount(unittest.TestCase):
    def test_none(self, _sinfo):
        retval = ""
        _sinfo.return_value = retval

        count = {}
        self.assertEqual(topology.cpu_count(), count)
        
    def test_single_node(self, _sinfo):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)"
        _sinfo.return_value = retval

        count = {"partition": 4}
        self.assertEqual(topology.cpu_count(), count)
        