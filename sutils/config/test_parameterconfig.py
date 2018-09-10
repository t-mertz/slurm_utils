import unittest
from collections import OrderedDict
import numpy as np

from . import parameterconfig
from ..parameters import numeric # points_range, step_range

class TestParameterConfig(unittest.TestCase):
    def test_empty_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {})


class TestIsParameter(unittest.TestCase):
    def test_empty_is_not_a_parameter(self):
        self.assertFalse(parameterconfig.is_parameter(""))
    
    def test_general_is_not_a_parameter(self):
        self.assertFalse(parameterconfig.is_parameter("general"))
    
    def test_pconfig_is_not_a_parameter(self):
        self.assertFalse(parameterconfig.is_parameter("pconfig"))
    
    def test_sbatch_is_not_a_parameter(self):
        self.assertFalse(parameterconfig.is_parameter("sbatch"))
    
    def test_par_is_a_parameter(self):
        self.assertTrue(parameterconfig.is_parameter("par-"))

    def test_par_abc_is_a_parameter(self):
        self.assertTrue(parameterconfig.is_parameter("par-abc"))

class TestGetParameterName(unittest.TestCase):
    def test_empty_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_name, "")
    
    def test_general_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_name, "general")

    def test_empty_parametername_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_name, "par-")
    
    def test_name_singlecharacter(self):
        self.assertEqual(parameterconfig.get_parameter_name("par-a"), "a")
    
    def test_name_fivecharacter(self):
        self.assertEqual(parameterconfig.get_parameter_name("par-gamma"), "gamma")
    
    def test_name_capital_singlecharacter(self):
        self.assertEqual(parameterconfig.get_parameter_name("par-B"), "B")
    
    def test_name_capital_threecharacter(self):
        self.assertEqual(parameterconfig.get_parameter_name("par-PHI"), "PHI")

    def test_name_mixedcase_fivecharacter(self):
        self.assertEqual(parameterconfig.get_parameter_name("par-Gamma"), "Gamma")

class TestSplitParameters(unittest.TestCase):
    def test_empty_has_no_parameters(self):
        config = OrderedDict()
        self.assertEqual(parameterconfig.split_parameters(config), OrderedDict())
    
    def test_no_parameters(self):
        config = OrderedDict([['a', None]])
        self.assertEqual(parameterconfig.split_parameters(config), OrderedDict())
    
    def test_single_parameter(self):
        config = OrderedDict([['par-a', None]])
        self.assertEqual(parameterconfig.split_parameters(config), OrderedDict([['a', None]]))
    
    def test_configsections_are_left_untouched(self):
        config = OrderedDict([['a', None]])
        parameterconfig.split_parameters(config)
        self.assertEqual(config, OrderedDict([['a', None]]))

    def test_parameters_are_removed(self):
        config = OrderedDict([['par-a', None]])
        parameterconfig.split_parameters(config)
        self.assertEqual(config, OrderedDict())

    def test_config_and_parameter_configsections_are_left_untouched(self):
        config = OrderedDict([['a', None], ['par-b', None]])
        parameterconfig.split_parameters(config)
        self.assertEqual(config, OrderedDict([['a', None]]))

    def test_config_and_parameter_parameters_contained_in_output(self):
        config = OrderedDict([['a', None], ['par-b', None]])
        self.assertEqual(parameterconfig.split_parameters(config), OrderedDict([['b', None]]))

class TestGetParameterType(unittest.TestCase):
    def test_empty_parameter_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {})
    
    def test_unknown_option_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'abc': None})
      
    def test_value_and_values_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'value': 0, 'values': 0})
    
    def test_value_and_lo_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'value': 0, 'lo': 0})
    
    def test_value_and_hi_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'value': 0, 'hi': 0})
    
    def test_value_and_points_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'value': 0, 'points': 0})
    
    def test_value_and_step_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'value': 0, 'step': 0})
    
    def test_values_and_lo_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'values': 0, 'lo': 0})
    
    def test_values_and_hi_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'values': 0, 'hi': 0})
    
    def test_values_and_points_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'values': 0, 'points': 0})
    
    def test_values_and_step_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'values': 0, 'step': 0})

    def test_points_and_step_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'lo': 0, 'hi': 0, 'points': 0, 'step': 0})

    def test_missing_lo_in_pointsrange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'hi': 0, 'points': 0})
    
    def test_missing_hi_in_pointsrange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'lo': 0, 'points': 0})
    
    def test_missing_lo_hi_in_pointsrange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'points': 0})
    
    def test_missing_points_step_in_range_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'hi': 0, 'lo': 0})
    
    def test_missing_lo_in_steprange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'hi': 0, 'step': 0})
    
    def test_missing_hi_in_steprange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'lo': 0, 'step': 0})
    
    def test_missing_lo_hi_in_steprange_raises_valueerror(self):
        self.assertRaises(ValueError, parameterconfig.get_parameter_type, {'step': 0})
    
    def test_value(self):
        self.assertEqual(parameterconfig.get_parameter_type({'value': 0}), parameterconfig.PARAMETER_TYPES['value'])
    
    def test_values(self):
        self.assertEqual(parameterconfig.get_parameter_type({'values': 0}), parameterconfig.PARAMETER_TYPES['values'])
    
    def test_pointsrange(self):
        self.assertEqual(parameterconfig.get_parameter_type({'lo': 0, 'hi': 0, 'points': 0}), parameterconfig.PARAMETER_TYPES['points-range'])
    
    def test_steprange(self):
        self.assertEqual(parameterconfig.get_parameter_type({'lo': 0, 'hi': 0, 'step': 0}), parameterconfig.PARAMETER_TYPES['step-range'])
    

class TestConstructParameter(unittest.TestCase):
    pass
    def test_value(self):
        self.assertEqual(
            parameterconfig.construct_parameter(
                parameterconfig.PARAMETER_TYPES['value'], {'value': "0"}
                ).values(),
                "0")

    def test_values(self):
        self.assertEqual(
            parameterconfig.construct_parameter(
                parameterconfig.PARAMETER_TYPES['values'], {'values': "0, 1, 2, 3"}
                ).values(),
                ["0", "1", "2", "3"])

    def test_pointsrange(self):
        self.assertTrue(
            np.all(parameterconfig.construct_parameter(
                parameterconfig.PARAMETER_TYPES['points-range'], {'lo': '0', 'hi': '1', 'points': '2'}
                ).values() == numeric.points_range(0, 1, 2))
        )

    def test_steprange(self):
        self.assertTrue(
            np.all(parameterconfig.construct_parameter(
                parameterconfig.PARAMETER_TYPES['step-range'], {'lo': '0', 'hi': '1', 'step': '0.1'}
                ).values() == numeric.step_range(0, 1, 0.1))
        )

class TestParseParameters(unittest.TestCase):
    pass