import unittest
from unittest.mock import Mock, patch

import numpy as np

from .. import api as slurm


@patch("sutils.slurm_interface.api._sinfo")
class TestSinfo(unittest.TestCase):
    def test_nooutput(self, _sinfo):
        _sinfo.return_value = ""

        res = slurm.SinfoResult("")
        self.assertEqual(slurm.sinfo()._data, res._data)

    def test_singleline(self, _sinfo):
        retval = "a b c d"
        _sinfo.return_value = retval

        res = slurm.SinfoResult(retval)
        self.assertEqual(slurm.sinfo()._data, res._data)


class TestSinfoResult(unittest.TestCase):
    def test_single_line_has_one_array_row(self):
        retval = "a b c d\n"

        res = slurm.SinfoResult(retval)
        self.assertTrue(np.all(res._data_array == np.array([["a", "b", "c", "d"]])))


class TestResult(unittest.TestCase):
    def test_empty_string_makes_empty_result(self):
        self.assertEqual(len(slurm.Result("")), 0)

class TestSinfoData(unittest.TestCase):
    def test_single_line(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        res = slurm.SinfoResult(retval)

        dat = {
            'node_names': np.array(["node01"]),
            'partitions': np.array(["partition"]),
            'loads': np.array([0.0]),
            'alloc_cpus': np.array([0]),
            'idle_cpus': np.array([4]),
            'other_cpus': np.array([0]),
            'all_cpus': np.array([4]),
            'sockets_per_node': np.array([1]),
            'cores_per_socket': np.array([4]),
            'threads_per_core': np.array([1]),
            'state': np.array(['idle']),
            'memory': np.array([8192]),
            'available_memory': np.array([8000]),
            'alloc_memory': np.array([0]),
            'features': np.array(['(null)']),
        }

        infodat = slurm.SinfoData(res)
        
        for key, val in dat.items():
            self.assertEqual(infodat._info_data[key], val)

    def test_two_lines(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)

        dat = {
            'node_names': np.array(["node01", "node02"]),
            'partitions': np.array(["partition", "partition1"]),
            'loads': np.array([0.0, 1.0]),
            'alloc_cpus': np.array([0, 7]),
            'idle_cpus': np.array([4, 8]),
            'other_cpus': np.array([0, 1]),
            'all_cpus': np.array([4, 16]),
            'sockets_per_node': np.array([1, 2]),
            'cores_per_socket': np.array([4, 8]),
            'threads_per_core': np.array([1, 2]),
            'state': np.array(['idle', 'alloc']),
            'memory': np.array([8192, 16384]),
            'available_memory': np.array([8000, 16000]),
            'alloc_memory': np.array([0, 10]),
            'features': np.array(['(null)', 'infiniband']),
        }

        infodat = slurm.SinfoData(res)
        
        for key, val in dat.items():
            self.assertTrue(np.all(infodat._info_data[key] == val))
