import unittest

import numpy as np

from . import util


class TestStringify(unittest.TestCase):
    def test_empty_list(self):
        lst = []
        self.assertEqual(util.stringify_list(lst), [])

    def test_list_of_ints(self):
        lst = [1, 2, 3]
        self.assertEqual(util.stringify_list(lst), ['1', '2', '3'])

    def test_list_of_negative_ints(self):
        lst = [-1, -2, -3]
        self.assertEqual(util.stringify_list(lst), ['-1', '-2', '-3'])

    def test_list_of_floats(self):
        lst = [1.123, 2.41, 3.51]
        self.assertEqual(util.stringify_list(lst), ['1.123', '2.41', '3.51'])

    def test_list_of_negative_floats(self):
        lst = [-1.123, -2.41, -3.51]
        self.assertEqual(util.stringify_list(lst), ['-1.123', '-2.41', '-3.51'])
    
    def test_list_of_strings(self):
        lst = ['a', 'b', 'c']
        self.assertEqual(util.stringify_list(lst), lst)

class TestIsFloat(unittest.TestCase):
    def test_bool(self):
        self.assertEqual(util.is_float(True), True)
        self.assertEqual(util.is_float(False), True)

    def test_int(self):
        self.assertEqual(util.is_float(1), True)
        self.assertEqual(util.is_float(-1), True)

    def test_float(self):
        self.assertEqual(util.is_float(1.), True)
        self.assertEqual(util.is_float(-1.), True)

    def test_string(self):
        self.assertEqual(util.is_float('abc'), False)

    def test_bool_arr(self):
        self.assertTrue(np.all(util.is_float([True, False]) == np.array([True, True])))

    def test_int_arr(self):
        self.assertTrue(np.all(util.is_float([1, -1]) == np.array([True, True])))

    def test_float_arr(self):
        self.assertTrue(np.all(util.is_float([1., -1.]) == np.array([True, True])))

    def test_string_arr(self):
        self.assertTrue(np.all(util.is_float(['abc', 'def']) == np.array([False, False])))

class TestMakeFloat(unittest.TestCase):
    def test_array(self):
        a = ['abc', 1, 2]
        self.assertTrue(np.all(util.make_float(a) == np.array([0., 1, 2])))

    def test_default_1(self):
        a = [1., 1, 2]
        self.assertTrue(np.all(util.make_float(a, default=1.) == np.array([1., 1, 2])))
