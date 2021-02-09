import unittest
import hpg
import random


class TestClientCommands(unittest.TestCase):
    def setUp(self):
        port = random.randint(20000, 50000)
        self.simulator = hpg.Simulator('localhost', port)
        self.client = hpg.ExtendedClient(hpg_monitoring_disabled=True)
        self.client.port = port
        self._test_count = 2

    def tearDown(self):
        self.simulator.stop()

    def resetValues(self, *args, **kwargs):
        self.client.temperature_min = kwargs.get('temperature_min', None)
        self.client.temperature_max = kwargs.get('temperature_max', None)
        self.client.active = kwargs.get('active', None) or False
        self.client.offtime = kwargs.get('offtime', random.uniform(1e8, 1e9))
        self.client.ontime_min = kwargs.get('ontime_min', None)
        self.client.ontime_max = kwargs.get('ontime_max', None)
        self.client.power_min = kwargs.get('power_min', None)
        self.client.power_max = kwargs.get('power_max', None)
        self.client.power_step = kwargs.get('power_step', None)
        self.client.power = kwargs.get('power', random.uniform(1e0, 1e3))
        self.client.ontime = kwargs.get('ontime', random.uniform(1e4, 1e8))

    def test_offtime(self):
        for offtime in [random.uniform(1e4, 1e6) for _ in range(self._test_count)]:
            with self.subTest('Test offtime', offtime=offtime):
                self.resetValues(ontime=offtime-1)
                self.client.offtime = offtime
                self.assertEqual(self.client.offtime, int(offtime))
            with self.assertRaises(ValueError):
                self.resetValues()
                self.client.offtime = -offtime

    def test_ontime(self):
        for ontime in [random.uniform(1e4, 1e6) for _ in range(self._test_count)]:
            with self.subTest('Test ontime', ontime=ontime):
                self.resetValues(ontime=ontime)
                self.assertEqual(self.client.ontime, int(ontime))
            with self.assertRaises(ValueError):
                self.resetValues()
                self.client.ontime = -ontime

    def test_active(self):
        for state in [True, False]:
            with self.subTest('Test active state', state=state):
                self.resetValues(active=state)
                self.assertIs(self.client.active, state)
                self.client.rf = 1
                if not state:
                    self.assertEqual(self.client.rf, 0)

    def test_power_step(self):
        for step in [random.uniform(0, 100) for _ in range(self._test_count)]:
            with self.subTest('Power step', step=step):
                self.resetValues(power_step=step)
                self.assertEqual(self.client.power_step, step)
        for step in [random.randint(1, 11) for _ in range(self._test_count)]:
            with self.subTest('Power step calculations', step=step):
                self.resetValues(power_step=step, active=True, power=step-1)
                self.assertEqual(self.client.power, step)
        self.resetValues()
        self.client.power_step = 0
        self.assertIsNone(self.client.power_step)

    def test_power(self):
        for power in [random.uniform(0, 100) for _ in range(self._test_count)] + [0]:
            with self.subTest('Test power', power=power):
                self.resetValues(active=True, power=power)
                self.assertEqual(self.client.power, power)

    def test_power_min(self):
        for power_min in [random.uniform(1e0, 1e2) for _ in range(self._test_count)]:
            with self.subTest('Power minimum', minimum=power_min):
                self.resetValues(power_min=power_min)
                self.assertEqual(self.client.power_min, power_min)
            with self.subTest('Power clamping', minimum=power_min):
                self.resetValues(active=True, power=power_min-0.1, power_min=power_min)
                self.assertEqual(self.client.power, power_min)
            with self.subTest('Special case', power=0, minium=power_min):
                self.resetValues(active=True, power_min=power_min, power=0)
                self.assertEqual(self.client.power, power_min)
                # self.client.power_step = power_min-0.1

    def test_power_max(self):
        for power_max in [random.uniform(1e0, 1e2) for _ in range(self._test_count)]:
            with self.subTest('Power maximum', maximum=power_max):
                self.resetValues(power_max=power_max)
                self.assertEqual(self.client.power_max, power_max)
            with self.subTest('Power clamping', maximum=power_max):
                self.resetValues(active=True, power=power_max+1, power_max=power_max)
                self.assertEqual(self.client.power, power_max)

    def test_temperatures(self):
        for temperature_max in [random.uniform(-273.15, 1e2) for _ in range(self._test_count)]:
            with self.subTest('Temperature maximum', maximum=temperature_max):
                self.resetValues(temperature_max=temperature_max)
                self.assertEqual(self.client.temperature_max, temperature_max)
        for temperature_min in [random.uniform(-273.15, 1e2) for _ in range(self._test_count)]:
            with self.subTest('Temperature minimum', maximum=temperature_min):
                self.resetValues(temperature_min=temperature_min)
                self.assertEqual(self.client.temperature_min, temperature_min)


if __name__ == '__main__':
    unittest.main()
