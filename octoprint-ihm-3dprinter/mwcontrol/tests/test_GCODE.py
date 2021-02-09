import unittest
import numpy as np
from mwcontrol.GCODE import *


class GCODETest(unittest.TestCase):
    def setUp(self):
        self.gcode = GCODE(log_console_enabled=True, logger_level='INFO')

    def tearDown(self):
        del self.gcode

    def test_G1(self):
        with self.subTest('No arguments'):
            self.assertFalse(self.gcode.G1([]))

        with self.subTest('Empty parameters'):
            self.assertFalse(self.gcode.G1(['X', 'Y', 'Z']))

        with self.subTest('Unsupported parameters'):
            with self.assertRaises(GCODEUnsupportedParameterError):
                self.gcode.G1(['A', 'B', 'C'])

        with self.subTest('Unsupported parameter values'):
            with self.assertRaises(GCODEFloatParameterError):
                self.gcode.G1(['X_', 'Yn', 'Z '])

        with self.subTest('Valid parameter and values'):
            self.assertTrue(self.gcode.G1(['X0', 'Y0', 'Z0.0 ']))

        with self.subTest('Position parser'):
            _target_position = np.array([1.1, 2, -3])
            self.gcode.G1(['X1.1', 'Y2', 'Z-3'])
            self.assertTrue(np.array_equal(self.gcode.gcode_travel_position, _target_position))

        with self.subTest('Distance calulation'):
            self.gcode.gcode_travel_distance = 0
            self.gcode.gcode_travel_position = np.zeros(3)
            self.gcode.G1(['X30', 'Y40', 'Z0'])
            self.assertEqual(self.gcode.gcode_travel_distance, 50)

    def test_G92(self):
        with self.subTest('Unsupported parameters'):
            with self.assertRaises(GCODEUnsupportedParameterError):
                self.gcode.G92(['A', 'B', 'C'])

        with self.subTest('Unsupported parameter values'):
            with self.assertRaises(GCODEFloatParameterError):
                self.gcode.G1(['X_', 'Yn', 'Z '])

        positions = [
            (['X1.1', 'Y2', 'Z-3'], np.array([1.1, 2, -3])),
            (['X0', 'Y0', 'Z0'], np.zeros(3)),
            ([], np.zeros(3)),
        ]
        for arguments, target in positions:
            with self.subTest(f'Set position {arguments}'):
                self.gcode.gcode_travel_position = np.random.rand(3)
                self.gcode.G92(arguments)
                self.assertTrue(np.array_equal(self.gcode.gcode_travel_position, target))

if __name__ == '__main__':
    unittest.main()
