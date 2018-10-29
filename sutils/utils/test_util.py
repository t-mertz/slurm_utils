import unittest

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
