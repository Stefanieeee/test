# coding=utf-8

import unittest
from hpg import Client, Simulator, UnkownCommandException
import random
import ipaddress


class TestClientCommands(unittest.TestCase):
    def setUp(self):
        port = random.randint(10000, 50000)
        self.simulator = Simulator('localhost', port)
        self.client = Client()
        self.client.port = port
        self._test_count = 5

    def tearDown(self):
        self.simulator.stop()

    def test_host(self):
        for hostname in ['0.0.0.0', '127.0.0.1', 'localhost']:
            with self.subTest('Set hostname property', hostname=hostname):
                self.client.host = hostname
                self.assertEqual(self.client.host, ipaddress.ip_address('127.0.0.1' if hostname == 'localhost' else hostname))
                self.assertTrue(self.client.is_available)

    def test_port(self):
        for port in [random.randint(10000, 50000) for _ in range(self._test_count)]:
            with self.subTest('Set port property', port=port):
                self.client.port = port
                self.assertIs(self.client.port, port)

    def test_mode(self):
        for mode in ['CW', 'PWM', 'NWA', 'NWA-PWM']:
            with self.subTest('Test valid modes', mode=mode):
                self.client.mode = mode
                self.assertEqual(self.client.mode, mode, f'Should be {mode}')
        for invalid_mode in ['PLASMA', 0, '', 'PWModulation']:
            with self.subTest('Test unsupported or invalid modes', mode=invalid_mode):
                with self.assertRaises(UnkownCommandException):
                    self.client.mode = invalid_mode

    def test_frequency(self):
        """Set the frequency and check responses for set and query commands"""
        for freq in [random.uniform(1e4, 1e10) for _ in range(self._test_count)] + [0] + ['1', '1.1']:
            with self.subTest('Set valid frequency', frequency=freq):
                self.client.frequency = int(float(freq))
                self.assertEqual(self.client.frequency, int(float(freq)))
        for freq in [-random.uniform(1e4, 1e10) for _ in range(self._test_count)] + ['', '_', 'Zero']:
            with self.subTest('Set invalid frequency', frequency=freq):
                with self.assertRaises(ValueError):
                    self.client.frequency = freq

    def test_power(self):
        limits = (-100, 100)
        values = []
        for _ in range(self._test_count):
            values += [random.randint(*limits), str(random.randint(*limits))]
            values += [random.uniform(*limits), str(random.uniform(*limits))]
        for power in values:
            power_reference = float(power)
            with self.subTest('Set power', power=power):
                if power_reference >= 0:
                    self.client.power = power
                    self.assertEqual(self.client.power, power_reference)
                else:
                    with self.assertRaises(ValueError):
                        self.client.power = power

    def test_rf(self):
        for state in [0, 1, '0', '1']:
            with self.subTest('Set RF state', state=state):
                self.client.rf = state
                self.assertIs(self.client.rf, 1 if int(float(state)) else 0)
        for invalid_state in [-1, -1.1, 2, 2.2, '_', 'ON']:
            with self.subTest('Set invalid RF state', state=invalid_state):
                with self.assertRaises(ValueError):
                    self.client.rf = invalid_state

    def test_ontime(self):
        limits = (-1e9, 1e9)
        values = []
        for _ in range(self._test_count):
            values += [random.randint(*limits), str(random.randint(*limits))]
            values += [random.uniform(*limits), str(random.uniform(*limits))]
        for ontime in values:
            ontime_reference = int(float(ontime))
            with self.subTest('Set ontime', ontime=ontime):
                if ontime_reference >= 0:
                    self.client.ontime = ontime
                    self.assertEqual(self.client.ontime, ontime_reference)
                else:
                    with self.assertRaises(ValueError):
                        self.client.ontime = ontime

    def test_offtime(self):
        limits = (-1e9, 1e9)
        values = []
        for _ in range(self._test_count):
            values += [random.randint(*limits), str(random.randint(*limits))]
            values += [random.uniform(*limits), str(random.uniform(*limits))]
        for offtime in values:
            offtime_reference = int(float(offtime))
            with self.subTest('Set offtime', offtime=offtime):
                if offtime_reference >= 0:
                    self.client.offtime = offtime
                    self.assertEqual(self.client.offtime, offtime_reference)
                else:
                    with self.assertRaises(ValueError):
                        self.client.offtime = offtime


if __name__ == '__main__':
    unittest.main()
