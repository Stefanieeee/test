import unittest
import random
from mwcontrol.BaseConnectionHandler import BaseConnectionHandler

class BaseConnectionHandlerSelfTest(unittest.TestCase):
    def setUp(self):
        self.connection = BaseConnectionHandler(autostart_flask=False)
        self.connection.connection_port = random.randrange(10000,20000,1)
        self.connection.connection_timeout = random.uniform(0.01,1)

    def tearDown(self):
        del self.connection

    def test_selftest(self):
        self.assertTrue(self.connection.test())

if __name__ == '__main__':
    unittest.main()
