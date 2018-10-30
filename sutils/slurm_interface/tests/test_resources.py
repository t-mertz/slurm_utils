import unittest
from unittest.mock import Mock, patch

from .. import resources
from .. import api as slurm

SINFO_STDOUT_TWO_LINE = "node01  partition  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                       +"node02  partition  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"

class TestCpuCount(unittest.TestCase):
    def test_none(self):
        retval = ""
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {}
        self.assertEqual(resources.cpu_count(data), count)
        
    def test_empty_lines_are_deleted(self):
        retval = "\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {}
        self.assertEqual(resources.cpu_count(data), count)
    
    def test_single_node(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {"node01": 4}
        self.assertEqual(resources.cpu_count(data), count)
        
    def test_two_nodes(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n" \
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        count = {"node01": 4, "node02": 4}
        self.assertEqual(resources.cpu_count(data), count)
        
class TestIsCPUCommensurate(unittest.TestCase):
    def test_5_is_not_commensurate_with_4(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertFalse(resources.is_cpu_commensurate(data, 5))

    def test_4_is_commensurate_with_4(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 4))
    
    def test_8_is_commensurate_with_4(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 8))

    def test_5_is_not_commensurate_with_4_idle(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertFalse(resources.is_cpu_commensurate(data, 5, status='idle'))

    def test_4_is_commensurate_with_4_idle(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 4, status='idle'))
    
    def test_8_is_commensurate_with_4_idle(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 8, status='idle'))

    def test_zero_cpus_is_commensurate(self):
        retval = "node01  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  0/4/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 0))

    def test_no_idle_is_not_commensurate(self):
        retval = "node01  partition  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
                +"node02  partition  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        data = slurm.SinfoData(slurm.SinfoResult(retval))

        self.assertTrue(resources.is_cpu_commensurate(data, 8, status='idle'))

class TestFindResources(unittest.TestCase):
    def test_zero_request_returns_zero(self):
        sinfo_data = slurm.SinfoData(SINFO_STDOUT_TWO_LINE)
        self.assertEqual(resources.find_resources(sinfo_data, 0), (0, 0))

    def test_single_cpu_returns_four(self):
        sinfo_data = slurm.SinfoData(SINFO_STDOUT_TWO_LINE)
        self.assertEqual(resources.find_resources(sinfo_data, 1), (4, 1))

    def test_four_cpus_returns_four(self):
        sinfo_data = slurm.SinfoData(SINFO_STDOUT_TWO_LINE)
        self.assertEqual(resources.find_resources(sinfo_data, 4), (4, 1))

    def test_too_many_cpus_returns_none(self):
        sinfo_data = slurm.SinfoData(SINFO_STDOUT_TWO_LINE)
        self.assertEqual(resources.find_resources(sinfo_data, 10), None)

class TestResource(unittest.TestCase):
    def test_partition_can_be_retrieved(self):
        res = resources.Resource('partition', 10, 2, None)
        self.assertEqual(res.partition(), 'partition')
    
    def test_cpus_can_be_retrieved(self):
        res = resources.Resource('partition', 10, 2, None)
        self.assertEqual(res.cpus(), 10)
    
    def test_nodes_can_be_retrieved(self):
        res = resources.Resource('partition', 10, 2, None)
        self.assertEqual(res.nodes(), 2)
    
    def test_mem_can_be_retrieved(self):
        res = resources.Resource('partition', 10, 2, 1000)
        self.assertEqual(res.memory(), 1000)
    
    # def test_zero_init_raises_ValueError(self):
    #     self.assertRaises(ValueError, resources.Resource, [])
    #     self.assertRaises(ValueError, resources.Resource, [0])

    # def test_list_of_three(self):
    #     res = resources.Resource([1, 2, 3])
    #     self.assertEqual(len(res), 3)

    def test_eq_returns_true_for_copy(self):
        res1 = resources.Resource('partition', 2, 3, None)
        res2 = resources.Resource('partition', 2, 3, None)

        self.assertEqual(res1, res2)

    def test_eq_returns_false_for_nonequal_nodes(self):
        res1 = resources.Resource('partition', 1, 3, None)
        res2 = resources.Resource('partition', 1, 2, None)

        self.assertNotEqual(res1, res2)
    
    def test_eq_returns_false_for_nonequal_cpus(self):
        res1 = resources.Resource('partition', 1, 3, None)
        res2 = resources.Resource('partition', 2, 3, None)

        self.assertNotEqual(res1, res2)

    def test_eq_returns_false_for_nonequal_partitions(self):
        res1 = resources.Resource('partition', 1, 3, None)
        res2 = resources.Resource('partition1', 1, 3, None)

        self.assertNotEqual(res1, res2)

    def test_eq_returns_false_for_nonequal_mem(self):
        res1 = resources.Resource('partition', 1, 3, 1000)
        res2 = resources.Resource('partition', 1, 3, 500)

        self.assertNotEqual(res1, res2)

    def test_repr_returns_dict(self):
        res = resources.Resource('mypartition', 12, 14, 100)
        self.assertEqual(repr(res), "<Resource object, partition=mypartition, cpus=12, nodes=14, mem=100>")

class TestSubsetInternal(unittest.TestCase):
    def test_empty_and_zero_returns_empty(self):
        self.assertEqual(resources._subset_internal([], 0), [])
    
    def test_empty_and_positive_returns_false(self):
        self.assertFalse(resources._subset_internal([], 1))
    
    def test_finite_and_zero_returns_empty(self):
        self.assertEqual(resources._subset_internal([1, 2, 3], 0), [])

    def test_n_eq_sum_returns_input(self):
        self.assertEqual(resources._subset_internal([2, 2], 4), [2, 2])
    
    def test_n_smaller_sum_returns_subset(self):
        self.assertEqual(resources._subset_internal([2, 2, 3, 4], 4), [4])

    def test_non_commensurate(self):
        self.assertEqual(resources._subset_internal([2, 2, 4], 5), [2, 4])

    def test_cluster_many(self):
        self.assertEqual(resources._subset_internal([16, 16, 16, 20, 20, 20], 48), [16, 16 ,16])
    
    def test_cluster_one(self):
        self.assertEqual(resources._subset_internal([16, 16, 16, 20, 20, 48], 48), [48])
    
    def test_cluster_incommensurate(self):
        self.assertEqual(sorted(resources._subset_internal([16, 16, 20, 20], 48)), [16, 16, 20])

    def test_xeon_cluster_48(self):
        self.assertEqual(sorted(resources._subset_internal(
            [16, 16, 16, 16, 16, 16, 16, 16, 16, 20, 20, 20, 20, 20, 20, 20, 24], 48)), [16, 16, 16])
    
    def test_xeon_cluster_24(self):
        self.assertEqual(sorted(resources._subset_internal(
            [16, 16, 16, 16, 16, 16, 16, 16, 16, 20, 20, 20, 20, 20, 20, 20], 24)), [16, 16])

    def test_big_cluster_48(self):
        self.assertEqual(sorted(resources._subset_internal(
            [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 64, 64, 64, 64, 24], 48)), [48])

    def test_big_cluster_64(self):
        self.assertEqual(sorted(resources._subset_internal(
            [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 64, 64, 64, 64, 24], 64)), [64])

    def test_big_cluster_200(self):
        self.assertEqual(sorted(resources._subset_internal(
            [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 64, 64, 64, 64, 24], 200)), [24, 48, 64, 64])


class TestGetMaximalResources(unittest.TestCase):
    def test_returns_single_resource(self):
        sinfo_data = slurm.SinfoData(SINFO_STDOUT_TWO_LINE)
        self.assertEqual(resources.get_maximal_resources(sinfo_data), {'partition': resources.Resource('partition', 8, 2, None)})

    def test_returns_multiple_resources(self):
        sout = "node01  partition1  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"\
               +"node02  partition2  0.00  4/0/0/4  1:4:1  idle  8192  8000  0  (null)\n"
        sinfo_data = slurm.SinfoData(sout)
        res = {'partition1': resources.Resource('partition1', 4, 1, None), 'partition2': resources.Resource('partition2', 4, 1, None)}
        self.assertEqual(resources.get_maximal_resources(sinfo_data), res)

    def test_returns_no_resource(self):
        sinfo_data = slurm.SinfoData('')
        self.assertEqual(resources.get_maximal_resources(sinfo_data), {})


