import unittest
from unittest.mock import Mock, patch
import subprocess

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

    def setUp(self):
        self.info_str = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                 +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"

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
        
    def test_array_shape(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        res = slurm.SinfoResult(retval)
        infodat = slurm.SinfoData(res)

         
        self.assertEqual(infodat['nodehost'].shape, (2,))
        self.assertEqual(infodat['partition'].shape, (2,))
        self.assertEqual(infodat['cpusload'].shape, (2,))
        self.assertEqual(infodat['alloccpus'].shape, (2,))
        self.assertEqual(infodat['idlecpus'].shape, (2,))
        self.assertEqual(infodat['othercpus'].shape, (2,))
        self.assertEqual(infodat['allcpus'].shape, (2,))
        self.assertEqual(infodat['sockets_per_node'].shape, (2,))
        self.assertEqual(infodat['cores_per_socket'].shape, (2,))
        self.assertEqual(infodat['threads_per_core'].shape, (2,))
        self.assertEqual(infodat['state'].shape, (2,))
        self.assertEqual(infodat['memory'].shape, (2,))
        self.assertEqual(infodat['freememory'].shape, (2,))
        self.assertEqual(infodat['allocmemory'].shape, (2,))
        self.assertEqual(infodat['features'].shape, (2,))

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

    def test_construct_from_string(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        
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

        infodat = slurm.SinfoData(retval)
        
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


    def test_mem_per_cpu(self):
        infodat = slurm.SinfoData(self.info_str)
        self.assertTrue(
            np.all(
                infodat.mem_per_cpu() == np.array([8192/4., 16384/16.])
            )
        )

    def test_freemem_per_idlecpu(self):
        infodat = slurm.SinfoData(self.info_str)
        self.assertTrue(
            np.all(
                infodat.freemem_per_idlecpu() == np.array([8000/4., 16000/8.])
            )
        )

    def test_filter_memory_0_returns_copy(self):
        infodat = slurm.SinfoData(self.info_str)

        filtered = infodat.filter_memory(0)
        
        self.assertEqual(infodat, filtered)

    def test_filter_memory_10000_returns_only_second_node(self):
        infodat = slurm.SinfoData(self.info_str)

        filtered = infodat.filter_memory(10000)
        infodat1 = slurm.SinfoData(self.info_str.split('\n')[1])
        
        self.assertEqual(infodat1, filtered)

    def test_copy_is_equal(self):
        infodat1 = slurm.SinfoData(self.info_str)
        infodat2 = slurm.SinfoData(self.info_str)

        self.assertEqual(infodat1, infodat2)
    
    def test_original_and_filtered_are_not_equal(self):
        infodat1 = slurm.SinfoData(self.info_str)
        infodat2 = infodat1.filter_cpus(5)

        self.assertNotEqual(infodat1, infodat2)

    def test_filter_idle(self):
        info_str = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node01  partition1  1.00  7/24/1/32  2:8:2  alloc  16384  16000  10  infiniband\n"\
                +"node02  partition1  1.00  32/0/0/32  2:8:2  alloc  16384  16000  10  infiniband\n"
        infodat = slurm.SinfoData(info_str)

        filtered = infodat.filter_idle()
        self.assertEqual(filtered, slurm.SinfoData(info_str.split('\n')[-1]))

    def test_filter_idle_returns_nodes_without_other(self):
        info_str = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node01  partition1  1.00  16/0/16/32  2:8:2  alloc  16384  16000  10  infiniband\n"\
                +"node02  partition1  1.00  32/0/0/32  2:8:2  alloc  16384  16000  10  infiniband\n"
        infodat = slurm.SinfoData(info_str)

        filtered = infodat.filter_idle()
        self.assertEqual(filtered, slurm.SinfoData(info_str.split('\n')[-1]))

class Test_sinfo_detail(unittest.TestCase):
    @patch("sutils.slurm_interface.api.sinfo")
    def test_calls_sinfo(self, sinfo):
        stdout = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition1  1.00  7/8/1/16  2:8:2  alloc  16384  16000  10  infiniband\n"
        sinfo.return_value = slurm.SinfoResult(stdout)
        slurm.sinfo_detail()
        sinfo.assert_called_once_with(format=slurm.SINFO_DETAIL_FORMAT, node=True, noheader=True)

    @patch("sutils.slurm_interface.api.run_command")
    def test_calls_runcommand_once(self, runcmd):
        runcmd.return_value = (0, u'', u'')
        slurm.sinfo_detail()
        runcmd.assert_called_once_with('sinfo', ['--Format', slurm.SINFO_DETAIL_FORMAT, '--Node', '--noheader'])

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

class TestRunCommand(unittest.TestCase):
    def test_return_code_0_for_ls(self):
        res = slurm.run_command('ls', [])
        self.assertEqual(res[0], 0)
    
    def test_return_code_0_for_ls_all(self):
        res = slurm.run_command('ls', ['-a'])
        self.assertEqual(res[0], 0)

    def test_return_code_1_for_unknown_command(self):
        cmd = 'myrandomcommandsurelydoesntexist'
        self.assertRaises(FileNotFoundError, slurm.run_command, cmd, [])

    def test_returns_stdout_as_string(self):
        cmd = 'ls'
        res = slurm.run_command(cmd, [])
        self.assertEqual(type(res[1]), str)

    def test_returns_stderr_as_string(self):
        cmd = 'ls'
        res = slurm.run_command(cmd, [])
        self.assertEqual(type(res[2]), str)

    @patch("subprocess.Popen")
    def test_popen_called(self, popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': (b'output', b'error')}
        process_mock.configure_mock(**attrs)
        popen.return_value = process_mock
        slurm.run_command('command', ['arg1'])
        popen.assert_called_once_with(['command', 'arg1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class TestSqueueUser(unittest.TestCase):
    @patch("sutils.slurm_interface.api._squeue")
    def test_calls_squeue_once(self, squeue):
        squeue.return_value = ''
        slurm.squeue_user()
        import getpass
        user = getpass.getuser()
        squeue.assert_called_once_with(['--user', user, '--noheader'])


class TestSqueue(unittest.TestCase):
    def setUp(self):
        self._stdout = "123456  partition1  jobname1   username1  PENDING  0:00  2  (Priority)\n"\
                     + "123457  partition2  jobname2   username2  RUNNING  1-01:41:13  4  partition1node[01-04]\n"

    @patch("sutils.slurm_interface.api._squeue")
    def test_calls_squeue_once(self, squeue):
        squeue.return_value = ''
        slurm.squeue([])
        squeue.assert_called_once_with([])

    @patch("sutils.slurm_interface.api._squeue")
    def test_returns_result_of_squeue(self, squeue):
        val = slurm.SqueueResult(self._stdout.split('\n')[0])
        squeue.return_value = self._stdout.split('\n')[0]
        res = slurm.squeue([])
        self.assertEqual(res, val)


class TestSqueueResult(unittest.TestCase):
    def setUp(self):
        self._stdout = "123456  partition1  jobname1   username1  PENDING  0:00  2  (Priority)\n"\
                     + "123457  partition2  jobname2   username2  RUNNING  1-01:41:13  4  partition1node[01-04]\n"
    

    def test_copy_is_equal(self):
        res1 = slurm.SqueueResult(self._stdout)
        res2 = slurm.SqueueResult(self._stdout)

        self.assertEqual(res1, res2)

    def test_empty_init(self):
        res = slurm.SqueueResult('')
        self.assertEqual(res._njobs, 0)

    def test_get_ids_returns_iterable(self):
        res1 = slurm.SqueueResult(self._stdout)

        self.assertTrue(hasattr(res1.get_ids(), '__iter__'))

    def test_get_ids_returns_iterable_for_empty_queue(self):
        res1 = slurm.SqueueResult("")

        self.assertTrue(hasattr(res1.get_ids(), '__iter__'))


class TestSbatchResult(unittest.TestCase):
    
    def test_stdout(self):
        stdout_str = "This is the stdout"
        
        self.assertEqual(slurm.SbatchResult(stdout_str).stdout(), stdout_str)
        