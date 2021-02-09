import unittest
from mwcontrol.Temperature import Temperature, NozzleTemperature
from mwcontrol.PIDMixin import PIDMixin
import random

class TestTemperature(unittest.TestCase):
    def setUp(self):
        self.t = Temperature(log_console_enabled=False)
        self.minimum_test_value = -300 # Temperature will neever go below this
        self.maximum_test_value = 1000 # Should be over 256 because python handles numbers differntly
        self.test_values_sample_size = 100

    def random_value(self):
        return random.uniform(self.minimum_test_value, self.maximum_test_value)

    def tearDown(self):
        del self.t

    def test_current_property(self):
        """Test the `current` property.

        """
        for value in [self.random_value() for _ in range(self.test_values_sample_size)]:
            with self.subTest(value=value):
                self.t.current = value
                self.assertEqual(self.t.current, value)

class TestNozzleTemperature(unittest.TestCase):
    def setUp(self):
        self.t = NozzleTemperature(log_console_enabled=False)

    def test_nothing(self):
        pass

    def tearDown(self):
        del self.t

class TestPIDMixin(unittest.TestCase):
    def setUp(self):
        self.p = PIDMixin(log_console_enabled=False)
        self.minimum_test_value = -300
        self.maximum_test_value = 1000
        self.test_values_sample_size = 100

    def random_value(self):
        return random.uniform(self.minimum_test_value, self.maximum_test_value)

    def tearDown(self):
        del self.p

    def test_pid_target(self):
        """Test the target property

        """
        for value in [self.random_value() for _ in range(self.test_values_sample_size)]:
            with self.subTest(value=value):
                self.p.pid_target = value
                self.assertEqual(self.p.pid_target, value)

    def test_pid_target_minimum(self):
        """Test functionality for the minimum value limit

        1. Test is the minimum can be set
        2. Test if the mimimum is enforced by setting a smaller value
        3. Test if the minimum can be disabled by setting it to `None`.
        """
        for minimum_value in [self.random_value() for _ in range(self.test_values_sample_size)]:
            with self.subTest(minimum_value=minimum_value):
                with self.subTest('Set the minimum target value'):
                    self.p.pid_target_minimum = minimum_value
                    self.assertEqual(self.p.pid_target_minimum, minimum_value)
                with self.subTest('Check minimum target value enforcement'):
                    self.p.pid_target = self.p.pid_target_minimum - 1
                    self.assertGreaterEqual(self.p.pid_target, self.p.pid_target_minimum)
                with self.subTest('Disable the minimum target value'):
                    self.p.pid_target_minimum = None
                    self.assertIsNone(self.p.pid_target_minimum)
                with self.subTest('Check if minimum really disabled'):
                    self.p.pid_target = minimum_value - 1
                    self.assertGreaterEqual(self.p.pid_target, minimum_value - 1)

    def test_pid_target_maximum(self):
        """Test functionality for the maximum value limit

        1. Test is the maximum can be set
        2. Test if the maximum is enforced by setting a larger value
        3. Test if the maximum can be disabled by setting it to `None`.

        """
        for maximum_value in [self.random_value() for _ in range(self.test_values_sample_size)]:
            with self.subTest(maximum_value=maximum_value):
                with self.subTest('Set the minimum target value'):
                    self.p.pid_target_maximum = maximum_value
                    self.assertEqual(self.p.pid_target_maximum, maximum_value)
                with self.subTest('Check minimum target value enforcement'):
                    self.p.pid_target = self.p.pid_target_maximum + 1
                    self.assertLessEqual(self.p.pid_target, self.p.pid_target_maximum)
                with self.subTest('Disable the minimum target value'):
                    self.p.pid_target_maximum = None
                    self.assertIsNone(self.p.pid_target_maximum)
                with self.subTest('Check if minimum really disabled'):
                    self.p.pid_target = maximum_value + 1
                    self.assertGreaterEqual(self.p.pid_target, maximum_value + 1)

    def test_pid_target_limits(self):
        """Cross-test limits.

        1. Test if the mimimum is always less or equal to the maximum
        2. Test if the maximum is always greater or equal to the minimum
        """
        for limit_value in [self.random_value() for _ in range(self.test_values_sample_size)]:
            with self.subTest(limit_value=limit_value):
                with self.subTest('Check minimum <= maximum'):
                    self.p.pid_target_maximum = limit_value
                    self.p.pid_target_minimum = limit_value + random.uniform(0,10)
                    self.assertLessEqual(self.p.pid_target_minimum, self.p.pid_target_maximum)
                with self.subTest('Check maximum >= minimum'):
                    self.p.pid_target_minimum = limit_value
                    self.p.pid_target_maximum = limit_value - random.uniform(0,10)
                    self.assertGreaterEqual(self.p.pid_target_maximum, self.p.pid_target_minimum)

if __name__ == '__main__':
    unittest.main()
