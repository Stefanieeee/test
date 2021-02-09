import unittest
import random
import logging
from mwcontrol.DataLoggerMixin import DataLoggerMixin
from mwcontrol.BaseController import WebServerMixin
from mwcontrol.LoggerMixin import LoggerMixin


class DataLogger(DataLoggerMixin, WebServerMixin, LoggerMixin):
    def __init__(self, *args, **kwargs):
        self.logger_configure(name='Datalogger', *args, **kwargs)
        super().__init__(*args, **kwargs)

class TestBaseController(unittest.TestCase):
    def setUp(self):
        self.datalogger = DataLogger(log_console_enabled=True, datalogger_backend='sqlite3')
        self.test_count = 2

    def tearDown(self):
        print(self.datalogger.datalogger_get('test'))
        self.datalogger._datalogger_stop()

    def test_basic(self):
        for value in [random.uniform(0,1e3) for _ in range(self.test_count)]:
            self.datalogger.datalogger_add('test', value)
        self.assertEqual(len(self.datalogger.datalogger_get('test')), self.test_count)

if __name__ == '__main__':
    unittest.main()
