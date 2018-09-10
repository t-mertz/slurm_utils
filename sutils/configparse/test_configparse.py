import unittest

from . import configparse
from . import cfgtypes


class TestIntType(unittest.TestCase):
    def test_empty(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "")

    def test_positive(self):
        self.assertEqual(cfgtypes.IntType("1").value(), 1)

    def test_negative(self):
        self.assertEqual(cfgtypes.IntType("-1").value(), -1)
    
    def test_nonint(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "1.1")

    def test_nonnumeric(self):
        self.assertRaises(ValueError, cfgtypes.IntType, "a")


class TestBoolType(unittest.TestCase):
    def test_empty(self):
        self.assertRaises(ValueError, cfgtypes.BoolType, "")
    
    def test_true_upper(self):
        self.assertEqual(cfgtypes.BoolType("True").value(), True)

    def test_true_lower(self):
        self.assertEqual(cfgtypes.BoolType("true").value(), True)
    
    def test_true_caps(self):
        self.assertEqual(cfgtypes.BoolType("TRUE").value(), True)

    def test_false_upper(self):
        self.assertEqual(cfgtypes.BoolType("False").value(), False)
    
    def test_false_lower(self):
        self.assertEqual(cfgtypes.BoolType("false").value(), False)
    
    def test_false_caps(self):
        self.assertEqual(cfgtypes.BoolType("FALSE").value(), False)

    def test_true_1(self):
        self.assertEqual(cfgtypes.BoolType("1").value(), True)
    
    def test_false_0(self):
        self.assertEqual(cfgtypes.BoolType("0").value(), False)
    
    def test_false_3(self):
        self.assertEqual(cfgtypes.BoolType("3").value(), False)
    
    def test_false_abc(self):
        self.assertEqual(cfgtypes.BoolType("abc").value(), False)

class TestOption(unittest.TestCase):
    pass

class TestGroup(unittest.TestCase):
    pass

class TestConfigParser(unittest.TestCase):
    def test_single_group(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, 1, required=False)
        parser = configparse.ConfigParser().add_section(group)
        res = parser.parse_config({'a': {'option1': "1"}})
        self.assertEqual(res['a']['option1'], 1)

    def test_single_group_empty_default(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, 1, required=False)
        parser = configparse.ConfigParser().add_section(group)
        res = parser.parse_config({})
        self.assertEqual(res['a']['option1'], 1)

    def test_single_group_default(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, 1, required=False)
        parser = configparse.ConfigParser().add_section(group)
        res = parser.parse_config({'a': {}})
        self.assertEqual(res['a']['option1'], 1)

    def test_single_group_option_required_nodefault(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True)
        parser = configparse.ConfigParser().add_section(group)
        self.assertRaises(RuntimeError, parser.parse_config, {'a': {}})

    def test_two_groups_name_collision_raises_runtimerror(self):
        group1 = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True)
        group2 = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True)
        parser = configparse.ConfigParser().add_section(group1)
        self.assertRaises(RuntimeError, parser.add_section, group2)
    
    def test_unknown_option_raises_runtime_error(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True)
        parser = configparse.ConfigParser().add_section(group)
        self.assertRaises(RuntimeError, parser.parse_config, {'a': {'option2': None}})

    def test_unknown_group_raises_runtime_error(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True)
        parser = configparse.ConfigParser().add_section(group)
        self.assertRaises(RuntimeError, parser.parse_config, {'b': None})


class TestStaticMethods(unittest.TestCase):
    def test_get_description_dict_single(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, required=True, desc="description_a1")
        parser = configparse.ConfigParser().add_section(group)
        self.assertEqual(configparse.get_description_dict(parser), {'a': {'option1': "description_a1"}})

    def test_get_default_dict_single(self):
        group = configparse.ConfigSection('a').add_option('option1', cfgtypes.IntType, 1, required=True, desc="description_a1")
        parser = configparse.ConfigParser().add_section(group)
        self.assertEqual(configparse.get_default_dict(parser), {'a': {'option1': 1}})

if __name__ == "__main__":
    unittest.main()