import unittest

from . import configparse
from . import cfgtypes


class TestOption(unittest.TestCase):
    def test_default_is_not_required(self):
        self.assertFalse(configparse.ConfigOption('name', cfgtypes.BaseType).is_required())

class TestSection(unittest.TestCase):
    def test_default_is_not_required(self):
        self.assertFalse(configparse.ConfigSection('name').is_required())
    
    def test_required_section_is_required(self):
        self.assertTrue(configparse.ConfigSection('name', required=True).is_required())
    
    def test_all_optional_section_is_not_required(self):
        sec = configparse.ConfigSection('name')
        sec.add_option('opt1', cfgtypes.BaseType).add_option('opt2', cfgtypes.BaseType)
        self.assertFalse(sec.is_required())

    def test_constructor_overrides_required_of_options(self):
        sec = configparse.ConfigSection('name', required=True)
        sec.add_option('opt1', cfgtypes.BaseType).add_option('opt2', cfgtypes.BaseType)
        self.assertTrue(sec.is_required())

    def test_one_required_section_is_required(self):
        sec = configparse.ConfigSection('name')
        sec.add_option('opt1', cfgtypes.BaseType, required=True).add_option('opt2', cfgtypes.BaseType)
        self.assertTrue(sec.is_required())

    def test_last_required_section_is_required(self):
        sec = configparse.ConfigSection('name')
        sec.add_option('opt1', cfgtypes.BaseType).add_option('opt2', cfgtypes.BaseType, required=True)
        self.assertTrue(sec.is_required())

    def test_all_required_section_is_required(self):
        sec = configparse.ConfigSection('name')
        sec.add_option('opt1', cfgtypes.BaseType, required=True).add_option('opt2', cfgtypes.BaseType, required=True)
        self.assertTrue(sec.is_required())

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