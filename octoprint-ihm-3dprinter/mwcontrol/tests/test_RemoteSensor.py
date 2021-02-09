import unittest
import random
import time
from mwcontrol.RemoteSensor import RemoteSensor, RemoteSensorSimulator, TemperatureSensor, FilamentSensor


class TestRemoteSensor(unittest.TestCase):
    def setUp(self):
        self.simulator = RemoteSensorSimulator()
        self.simulator.connection_port = random.randrange(10000,20000,1)
        self.simulator.connection_timeout = random.uniform(0.01,1)

    def tearDown(self):
        self.simulator.stop()
        del self.simulator

class TestRemoteTemperatureSensor(TestRemoteSensor):
    def setUp(self):
        super().setUp()
        self.sensor = TemperatureSensor()
        self.sensor.connection_port = self.simulator.connection_port
        self.sensor.connection_timeout = random.uniform(0.01,1)
        self.sensor.bind()

    def tearDown(self):
        self.sensor.stop()
        del self.sensor
        super().tearDown()

    def test_temperature(self):
        value = random.uniform(20, 300)
        self.sensor.send_message(f'TEMP {value}')
        time.sleep(0.1)
        self.assertEqual(self.sensor.temperature, value)

class TestRemoteFilamentSensor(TestRemoteSensor):
    def setUp(self):
        super().setUp()
        self.sensor = FilamentSensor()
        self.sensor.connection_port = self.simulator.connection_port
        self.sensor.connection_timeout = random.uniform(0.01,1)
        self.sensor.bind()

    def tearDown(self):
        self.sensor.stop()
        del self.sensor
        super().tearDown()

    def test_temperature(self):
        value = random.uniform(20, 300)
        self.sensor.send_message(f'STEP {value}')
        time.sleep(0.1)
        self.assertEqual(self.sensor.step, value)

if __name__ == '__main__':
    unittest.main()
