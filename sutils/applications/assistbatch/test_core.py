import unittest
from unittest.mock import patch, mock_open, MagicMock, Mock, call

from ...slurm_interface import resources as resources
from ...slurm_interface import api as slurm
from . import core

def my_mock_open(*args, **kwargs):
    f_open = mock_open(*args, **kwargs)
    f_open.return_value.__iter__ = lambda self: iter(self.readline, '')
    return f_open

class TestGetResourceSummary(unittest.TestCase):
    def test_print_none(self):
        idle = []
        queued = []
        self.assertEqual(core.get_resource_summary(idle, queued), [])
        
    def test_print_one_idle(self):
        idle = [resources.Resource('partition', 2, 1, None)]
        queued = []
        ret = ["(1) partition:       partition, CPUs:    2, nodes:  1, (idle)\n"]
        self.assertEqual(core.get_resource_summary(idle, queued), ret)

    def test_print_one_queued(self):
        idle = []
        queued = [resources.Resource('partition', 2, 1, None)]
        ret = ["(1) partition:       partition, CPUs:    2, nodes:  1, (pending)\n"]
        self.assertEqual(core.get_resource_summary(idle, queued), ret)

    def test_print_two_idle_queued(self):
        idle = [resources.Resource('partition3', 4, 2, None),
                resources.Resource('partition4', 1, 2, None)
               ]
        queued = [resources.Resource('partition', 2, 1, None),
                  resources.Resource('partition1', 3, 1, None)
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

    @patch("sutils.applications.assistbatch.core.slurm.SinfoData.filter_partition")
    def test_calls_filter_partition(self, filter_partition):
        req = resources.Resource('partition', 1, 1, None)
        filter_partition.return_value = slurm.SinfoData(self.sinfo_stdout.split('\n')[0])
        core.find_optimal_resources(self.infodat, req, idle=True)

        filter_partition.assert_called_once_with(['partition'])
    
    @patch("sutils.applications.assistbatch.core.resources.find_resources")
    @patch("sutils.applications.assistbatch.core.slurm.SinfoData.filter_partition")
    def test_calls_find_resources(self, filter_partition, find_resources):
        part_infodat = slurm.SinfoData(self.sinfo_stdout.split('\n')[0])
        filter_partition.return_value = part_infodat
        find_resources.return_value = [1, 2]

        req = resources.Resource('partition', 1, 1, None)
        core.find_optimal_resources(self.infodat, req, idle=True)

        find_resources.assert_called_once_with(part_infodat, 1, idle=True)

    @patch("sutils.applications.assistbatch.core.resources.find_resources")
    def test_returns_optimal_resource(self, find_resources):
        find_resources.return_value = (10, 2)
        req = resources.Resource('partition', 1, 1, None)
        ret = core.find_optimal_resources(self.infodat, req, idle=True)
        opt = resources.Resource('partition', 10, 2, None)
        self.assertEqual(ret, [opt])

SAMPLE_FILE = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --partition=mypartition\n",
    "#SBATCH --ntasks=20\n",
    "sleep 1\n"
])

SAMPLE_FILE_NODES = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --partition=mypartition\n",
    "#SBATCH --ntasks=20\n",
    "#SBATCH --nodes=2\n",
    "sleep 1\n"
])

SAMPLE_FILE_MEM = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --partition=mypartition\n",
    "#SBATCH --ntasks=20\n",
    "#SBATCH --nodes=2\n",
    "#SBATCH --mem=2000\n",
    "sleep 1\n"
])

SAMPLE_FILE_TWO_PARTITIONS = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --partition=mypartition,mysecondpartition\n",
    "#SBATCH --ntasks=20\n",
    "sleep 1\n"
])

SAMPLE_FILE_MISSING_PARTITION = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --ntasks=20\n",
    "sleep 1\n"
])

SAMPLE_FILE_MISSING_NTASKS = ''.join([
    "#!/bin/sh\n",
    "#SBATCH --partition=mypartition\n",
    "sleep 1\n"
])

class TestReadSbatchFile(unittest.TestCase):
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_MISSING_PARTITION), create=True)
    def test_missing_partition_raises_runtimeerror(self):
        self.assertRaises(RuntimeError, core.read_sbatch_file, 'filename')
    
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_MISSING_NTASKS), create=True)
    def test_missing_ntasks_raises_runtimeerror(self):
        self.assertRaises(RuntimeError, core.read_sbatch_file, 'filename')
    
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_reads_single_partition_correctly(self):
        res = resources.Resource('mypartition', 20, None, None)
        self.assertEqual(core.read_sbatch_file('filename')[0], res)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_returns_single_partition(self):
        self.assertEqual(len(core.read_sbatch_file('filename')), 1)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_TWO_PARTITIONS), create=True)
    def test_returns_two_partitions(self):
        self.assertEqual(len(core.read_sbatch_file('filename')), 2)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_TWO_PARTITIONS), create=True)
    def test_reads_two_partitions_correctly(self):
        res1 = resources.Resource('mypartition', 20, None, None)
        res2 = resources.Resource('mysecondpartition', 20, None, None)
        self.assertEqual(core.read_sbatch_file('filename'), [res1, res2])
    
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_NODES), create=True)
    def test_reads_nodes_correctly(self):
        self.assertEqual(core.read_sbatch_file('filename')[0].nodes(), 2)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_MEM), create=True)
    def test_reads_mem_correctly(self):
        self.assertEqual(core.read_sbatch_file('filename')[0].memory(), 2000)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_missing_nodes_is_none(self):
        self.assertEqual(core.read_sbatch_file('filename')[0].nodes(), None)


# @patch("sutils.applications.assistbatch.core.slurm.sinfo_detail", Mock())
# class TestSubmit(unittest.TestCase):
#     @patch("sutils.applications.assistbatch.core.read_sbatch_file")
#     def test_calls_read_sbatch_file(self, read):
#         core.submit('myfilename')
#         read.assert_called_once_with('myfilename')

class TestWriteSbatchFile(unittest.TestCase):
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_calls_open_read_once(self):
        #myopen =  my_mock_open(read_data=SAMPLE_FILE)
        core.write_sbatch_file('infilename', resources.Resource('partition', 1, 1, 1000))
        self.assertEqual(core.open.mock_calls.count(call('infilename', 'r')), 1)
    
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_calls_open_write_once(self):
        #myopen =  my_mock_open(read_data=SAMPLE_FILE)
        core.write_sbatch_file('infilename', resources.Resource('partition', 1, 1, 1000))
        self.assertEqual(core.open.mock_calls.count(call('outfilename', 'w')), 1)
    
    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE), create=True)
    def test_calls_write_once_per_line(self):
        #myopen =  my_mock_open(read_data=SAMPLE_FILE)
        core.write_sbatch_file('infilename', resources.Resource('mynewpartition', 1, 1, 1000))
        calls = [
            call('infilename', 'r'),
            call().__enter__(),
            call('outfilename', 'w'),
            call().__enter__(),
            call().readline(),
            call().write("#!/bin/sh\n"),
            call().readline(),
            call().write("#SBATCH --partition=mynewpartition\n"),
            call().readline(),
            call().write("#SBATCH --ntasks=1\n"),
            call().readline(),
            call().write("#SBATCH --nodes=1\n"),
            call().write("sleep 1\n"),
            call().readline(),
            call().__exit__(None, None, None),
            call().__exit__(None, None, None)
        ]
        core.open.assert_has_calls(calls)
        

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_NODES), create=True)
    def test_calls_write_once_per_line_with_nodes(self):
        #myopen =  my_mock_open(read_data=SAMPLE_FILE)
        core.write_sbatch_file('infilename', resources.Resource('mynewpartition', 1, 1, 1000))
        calls = [
            call('infilename', 'r'),
            call().__enter__(),
            call('outfilename', 'w'),
            call().__enter__(),
            call().readline(),
            call().write("#!/bin/sh\n"),
            call().readline(),
            call().write("#SBATCH --partition=mynewpartition\n"),
            call().readline(),
            call().write("#SBATCH --ntasks=1\n"),
            call().readline(),
            call().write("#SBATCH --nodes=1\n"),
            call().readline(),
            call().write("sleep 1\n"),
            call().readline(),
            call().__exit__(None, None, None),
            call().__exit__(None, None, None)
        ]
        core.open.assert_has_calls(calls)

    @patch("sutils.applications.assistbatch.core.open", my_mock_open(read_data=SAMPLE_FILE_MEM), create=True)
    def test_calls_write_once_per_line_with_mem(self):
        #myopen =  my_mock_open(read_data=SAMPLE_FILE)
        core.write_sbatch_file('infilename', resources.Resource('mynewpartition', 1, 1, 1000))
        calls = [
            call('infilename', 'r'),
            call().__enter__(),
            call('outfilename', 'w'),
            call().__enter__(),
            call().readline(),
            call().write("#!/bin/sh\n"),
            call().readline(),
            call().write("#SBATCH --partition=mynewpartition\n"),
            call().readline(),
            call().write("#SBATCH --ntasks=1\n"),
            call().readline(),
            call().write("#SBATCH --nodes=1\n"),
            call().readline(),
            call().write("#SBATCH --mem=1000\n"),
            call().readline(),
            call().write("sleep 1\n"),
            call().readline(),
            call().__exit__(None, None, None),
            call().__exit__(None, None, None)
        ]
        core.open.assert_has_calls(calls)
