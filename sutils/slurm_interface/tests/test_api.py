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
    def test_empty_constructor(self):
        infodat = slurm.SinfoData()
        
        dat = {
            'nodehost': np.array([], dtype=np.unicode_),
            'partition': np.array([], dtype=np.unicode_),
            'cpusload': np.array([], dtype=float),
            'alloccpus': np.array([], dtype=int),
            'idlecpus': np.array([], dtype=int),
            'othercpus': np.array([], dtype=int),
            'allcpus': np.array([], dtype=int),
            'sockets_per_node': np.array([], dtype=int),
            'cores_per_socket': np.array([], dtype=int),
            'threads_per_core': np.array([], dtype=int),
            'state': np.array([], dtype=np.unicode_),
            'memory': np.array([], dtype=int),
            'freememory': np.array([], dtype=int),
            'allocmemory': np.array([], dtype=int),
            'features': np.array([], dtype=np.unicode_),
        }
        for key, val in dat.items():
            self.assertTrue(np.all(infodat._info_data[key]==val))

    def test_copy_constructor(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)

        infodat1 = slurm.SinfoData(infodat)

        for key, val in infodat1._info_data.items():
            self.assertTrue(np.all(infodat._info_data[key]==val))
        
    def test_single_line(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        res = slurm.SinfoResult(retval)

        dat = {
            'nodehost': np.array(["node01"]),
            'partition': np.array(["partition"]),
            'cpusload': np.array([0.0]),
            'alloccpus': np.array([0]),
            'idlecpus': np.array([4]),
            'othercpus': np.array([0]),
            'allcpus': np.array([4]),
            'sockets_per_node': np.array([1]),
            'cores_per_socket': np.array([4]),
            'threads_per_core': np.array([1]),
            'state': np.array(['idle']),
            'memory': np.array([8192]),
            'freememory': np.array([8000]),
            'allocmemory': np.array([0]),
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
            'nodehost': np.array(["node01", "node02"]),
            'partition': np.array(["partition", "partition1"]),
            'cpusload': np.array([0.0, 1.0]),
            'alloccpus': np.array([0, 7]),
            'idlecpus': np.array([4, 8]),
            'othercpus': np.array([0, 1]),
            'allcpus': np.array([4, 16]),
            'sockets_per_node': np.array([1, 2]),
            'cores_per_socket': np.array([4, 8]),
            'threads_per_core': np.array([1, 2]),
            'state': np.array(['idle', 'alloc']),
            'memory': np.array([8192, 16384]),
            'freememory': np.array([8000, 16000]),
            'allocmemory': np.array([0, 10]),
            'features': np.array(['(null)', 'infiniband']),
        }

        infodat = slurm.SinfoData(res)
        
        for key, val in dat.items():
            self.assertTrue(np.all(infodat._info_data[key] == val))

    def test_getitem_hit(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)
        for key in ['nodehost', 'partition', 'cpusload', 'alloccpus', 
                    'idlecpus', 'othercpus', 'allcpus', 
                    'sockets_per_node', 'cores_per_socket', 
                    'threads_per_core', 'state', 'memory', 'freememory',
                    'allocmemory', 'features']:
            self.assertIn(key, infodat)

    def test_getitem_miss(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)
        self.assertRaises(KeyError, infodat.__getitem__, 'abc')

    def test_filter_one_partition(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)

        res = infodat.filter_partition(['partition'])
        dat = {
            'nodehost': np.array(["node01"]),
            'partition': np.array(["partition"]),
            'cpusload': np.array([0.0]),
            'alloccpus': np.array([0]),
            'idlecpus': np.array([4]),
            'othercpus': np.array([0]),
            'allcpus': np.array([4]),
            'sockets_per_node': np.array([1]),
            'cores_per_socket': np.array([4]),
            'threads_per_core': np.array([1]),
            'state': np.array(['idle']),
            'memory': np.array([8192]),
            'freememory': np.array([8000]),
            'allocmemory': np.array([0]),
            'features': np.array(['(null)']),
        }

        for key, val in dat.items():
            self.assertTrue(np.all(res._info_data[key] == val))

    def test_filter_cpus_ge5(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)

        filtered = infodat.filter_cpus(5)
        dat = {
            'nodehost': np.array(["node02"]),
            'partition': np.array(["partition1"]),
            'cpusload': np.array([1.0]),
            'alloccpus': np.array([7]),
            'idlecpus': np.array([8]),
            'othercpus': np.array([1]),
            'allcpus': np.array([16]),
            'sockets_per_node': np.array([2]),
            'cores_per_socket': np.array([8]),
            'threads_per_core': np.array([2]),
            'state': np.array(['alloc']),
            'memory': np.array([16384]),
            'freememory': np.array([16000]),
            'allocmemory': np.array([10]),
            'features': np.array(['infiniband']),
        }
        
        for key, val in dat.items():
            self.assertTrue(np.all(filtered._info_data[key] == val))


class Test_sinfo_detail(unittest.TestCase):
    @patch("sutils.slurm_interface.api.sinfo")
    def test_calls_sinfo(self, sinfo):
        stdout = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        sinfo.return_value = slurm.SinfoResult(stdout)
        slurm.sinfo_detail()
        sinfo.assert_called_once_with(format=slurm.SINFO_DETAIL_FORMAT, node=True, noheader=True)

    @patch("sutils.slurm_interface.api.sinfo")
    def test_returns_processed_sinforesult(self, sinfo):
        stdout = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        sinfo.return_value = slurm.SinfoResult(stdout)
        retval = slurm.sinfo_detail()
        dat = {
            'nodehost': np.array(["node01", "node02"]),
            'partition': np.array(["partition", "partition1"]),
            'cpusload': np.array([0.0, 1.0]),
            'alloccpus': np.array([0, 7]),
            'idlecpus': np.array([4, 8]),
            'othercpus': np.array([0, 1]),
            'allcpus': np.array([4, 16]),
            'sockets_per_node': np.array([1, 2]),
            'cores_per_socket': np.array([4, 8]),
            'threads_per_core': np.array([1, 2]),
            'state': np.array(['idle', 'alloc']),
            'memory': np.array([8192, 16384]),
            'freememory': np.array([8000, 16000]),
            'allocmemory': np.array([0, 10]),
            'features': np.array(['(null)', 'infiniband']),
        }
        for key, val in dat.items():
            self.assertTrue(np.all(retval._info_data[key] == val))
