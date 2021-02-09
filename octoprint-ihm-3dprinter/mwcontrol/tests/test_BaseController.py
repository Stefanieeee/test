import unittest
import random
from mwcontrol.BaseController import *

class TestBaseController(unittest.TestCase):
    def setUp(self):
        self.base = BaseController(log_console_enabled=False)
        self.test_count = 10

    def tearDown(self):
        del self.base

    def test_log_level(self):
        """Test the `log_level` property

        """
        self.base.log_level = 'INFO'
        self.assertEqual(self.base.log_level, 'INFO')
        self.base.log_level = 'DEBUG'
        self.assertEqual(self.base.log_level, 'DEBUG')

    def test_unit_temperature(self):
        """Test the temperature unit setting
        """
        for code in self.base.unit_temperature_valid:
            with self.subTest(code=code):
                self.base.unit_temperature = code
                self.assertEqual(self.base.unit_temperature, code)

    def test_check_temperature_clamp(self):
        minimums = {'K': 0, 'C': -273.15, 'F': -459.670}
        for unit in self.base.unit_temperature_valid:
            self.base.unit_temperature = unit
            with self.subTest(unit=self.base.unit_temperature):
                result = self.base.check_temperature(minimums[unit]-1.0, True)
                self.assertEqual(result, minimums[unit])
                for _ in range(self.test_count):
                    value = random.uniform(minimums[unit], 1000)
                    with self.subTest(value=value):
                        self.assertEqual(self.base.check_temperature(value), value)
                        with self.assertRaises(CheckValueException):
                            self.base.check_temperature(minimums[unit]-1.0)

    def test_minimum_value(self):
        for _ in range(self.test_count):
            value = random.uniform(-1, 1)
            self.assertEqual(self.base._value_check_minimum(value), value)
            self.assertEqual(self.base._value_check_minimum(value,value), value)
            with self.assertRaises(CheckValueException):
                self.base._value_check_minimum(value, value, exclusive=True)
            with self.assertRaises(CheckValueException):
                self.base._value_check_minimum(value-1.0, value)
            self.assertEqual(self.base._value_check_minimum(value-1.0,value, True), value)

    def test_maximum_value(self):
        for _ in range(self.test_count):
            value = random.uniform(-1, 1)
            self.assertEqual(self.base._value_check_maximum(value), value)
            self.assertEqual(self.base._value_check_maximum(value,value), value)
            with self.assertRaises(CheckValueException):
                self.base._value_check_maximum(value, value, exclusive=True)
            with self.assertRaises(CheckValueException):
                self.base._value_check_maximum(value+1.0, value)
            self.assertEqual(self.base._value_check_maximum(value+1.0, value, True), value)

    def test_interval(self):
        with self.subTest('Test arguments'):
            with self.assertRaises(ArgumentException):
                self.base._value_check_interval(0, (2,-1))
        for _ in range(self.test_count):
            value = random.uniform(-1, 1)
            span = (value, value)
            clamp = (True, True)
            self.assertEqual(self.base._value_check_interval(value), value)
            self.assertEqual(self.base._value_check_interval(value, span), value)
            self.assertEqual(self.base._value_check_interval(value+1.0, span, clamp), value)
            self.assertEqual(self.base._value_check_interval(value-1.0, span, clamp), value)


if __name__ == '__main__':
    unittest.main()
