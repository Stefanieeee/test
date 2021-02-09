import time
import threading
from tinydb import TinyDB, Query
from .LoggerMixin import LoggerMixin
import sqlite3
import collections
import csv
import os
import io
import logging


"""数据记录模块将所有值记录到sqlite3内存数据库中每次调用控制功能
   每个模块都可以自定义提供给数据记录器的数据
   记录后 数据以.CSV的格式保存在内存中
"""


def flatten(d, parent_key=''):

    items = []

    for key, value in d.items():
        new_key = parent_key + '_' + key if parent_key else key

        if isinstance(value, collections.MutableMapping):
            items.extend(flatten(value, new_key).items())

        else:
            items.append((new_key, value))

    return dict(items)


class DataLoggerFile():

    def __init__(self, name, records):

        self.data = ''
        self.name = name
        self.records = records


class DataLoggerMixin(LoggerMixin):

    def __init__(self, *args, **kwargs):

        """Class constructor
        """

        super().__init__(*args, **kwargs)
        self.datalogger_current = {}

        """ 多线程并发
            可以使一个线程等待其他线程的通知
        """
        self.__dump_event = threading.Event()
        self.__start_event = threading.Event()
        self.__stop_event = threading.Event()
        self.__is_running = threading.Event()
        self.__logger = logging.getLogger('MCS.Datalogger')
        self.__logger.info('Initialize DataLoggerMixin')
        self.__files = {}

    ################
    # Classmethods #
    ################
    """读取默认值
    """
    @classmethod
    def get_defaults(cls):

        return {
            'active': False,
            'index': 0,
            'start_date': None,
            'stop_date': None,
            'stop_count': 1e9,
            'backend': 'sqlite3',
            'data_dir': '.',
            'table_name': 'datalogger',
            'delimiter': ';',
            'clear_on_export': True
        }

    ##############
    # Properties #
    ##############

    @property
    def datalogger_status(self):

        status = self._settings['datalogger'].copy()
        status['start_date'] = None
        status['stop_date'] = None
        status['files'] = [key for key, value in self.__files.items()]
        return status

    @property
    def __delimiter(self) -> str:

        return self._settings['datalogger']['delimiter']

    @__delimiter.setter
    def __delimiter(self, delimiter: str):

        self._settings['datalogger']['delimiter'] = delimiter

    @property
    def __clear_on_export(self) -> bool:

        return self._settings['datalogger']['clear_on_export']

    @__clear_on_export.setter
    def __clear_on_export(self, clear_flag: bool):

        self._settings['datalogger']['clear_on_export'] = clear_flag

    @property
    def __index(self):

        return self._settings['datalogger']['index']

    @__index.setter
    def __index(self, value):

        try:
            value = int(value)

        except ValueError:
            pass

        self._settings['datalogger']['index'] = value

    @property
    def datalogger_files(self) -> list:
        return self.__files

    @property
    def datalogger_backend(self) -> str:

        return self._settings['datalogger']['backend']

    @datalogger_backend.setter
    def datalogger_backend(self, backend_name: str):

        try:
            backend_name = str(backend_name)
        except ValueError:
            backend_name = None

        if backend_name not in ['tinydb', 'sqlite3']:
            self.__logger.error(f'Backend {backend_name} is not supported!')
            return

        self._settings['datalogger']['backend'] = backend_name
        self.__logger.info(f'Use {self.datalogger_backend} for datalogger')

    @property
    def datalogger_active(self):

        return self.__is_running.is_set()

    @property
    def __table_name(self):

        return self._settings['datalogger']['table_name']

    ###########
    # Methods #
    ###########

    def update_settings(self, settings: dict = {}, *args, **kwargs):

        """Update settings
        :param settings: A dictionary with all settings for this instance
        :type settings: dict, optional
        """

        super().update_settings(settings=settings, *args, **kwargs)
        # TODO: Use instance internal settings here

        if 'datalogger' not in self._settings:
            self._settings['datalogger'] = DataLoggerMixin.get_defaults()
            settings = self._settings['datalogger'].copy()  # Trigger the updates
            self.__logger.info('Load default settings for DataLoggerMixin')

        if 'datalogger' not in settings:
            return

        if 'start_date' in settings['datalogger']:
            self.__start_date = settings['datalogger']['start_date']

        if 'stop_date' in settings['datalogger']:
            self.__stop_date = settings['datalogger']['stop_date']

        if 'stop_count' in settings['datalogger']:
            self.__stop_count = settings['datalogger']['stop_count']

    def datalogger_stop(self):

        """Stop the datalogger
        This will set a flag so the main datalogger loop can react accordingly.
        """

        if self.datalogger_active:
            self.__stop_event.set()
            self.__logger.info('Receive STOP command')
        else:
            self.__logger.error('Stop failed: datalogger is not running')

    def datalogger_start(self):

        """Start the datalogger
        This will set a flag so the main datalogger loop can react accordingly.
        """

        if not self.datalogger_active:
            self.__stop_event.clear()
            self.__start_event.set()
            self.__dump_event.clear()
        else:
            self.__logger.error('Start failed: datalogger is already running')




    def datalogger_dump(self, delimiter: str = ';', clear_database: bool = True):

        """Export all data to a CSV file
        This will set a flag so the main datalogger loop can react accordingly.
        """

        if self.datalogger_active:
            self.__dump_event.set()
        else:
            self.__logger.error('Export failed: datalogger is not running')

    def datalogger_run(self):

        """Main datalogger method
        This method should be hooked in a thread and the datalogger controlled
        through the start/stop/dump events.
        """

        self._settings['datalogger']['active'] = self.datalogger_active
        self._settings['datalogger']['data_dir'] = self.data_dir

        if not self.datalogger_active:

            if self.__start_date is not None:
                if time.time() > self.__start_date:
                    self.__start_event.set()

            if self.__start_event.is_set():
                self.__setup()
                self.__start_event.clear()
            else:
                return  # Do nothing is datalogger is not enabled

        # Add values to the database
        self.__add_multiple(self.datalogger_current)

        # stop the datalogger if a maximum count is set and reached
        if self.__stop_count is not None:
            if self.__index > self.__stop_count:
                self.__stop_event.set()
        # stop the datalogger if a maximum time is set and reached
        elif self.__stop_date is not None:
            if time.time() > self.__stop_date:
                self.__stop_event.set()

        # Dismantle datalogger if deactivated
        if self.__stop_event.is_set():
            self.__close()
            self.__stop_event.clear()
        # Perform DB dump if required
        elif self.__dump_event.is_set():
            self.__export_to_csv()
            self.__dump_event.clear()

    ####################
    # Internal methods #
    ####################

    def __setup(self):

        """Setup the database based on the configured backend.
        """

        if self.datalogger_backend == 'sqlite3':
            self.__setup_sqlite3()
        elif self.datalogger_backend == 'tinydb':
            self.__setup_tinydb()

        self.__is_running.set()

        if self.__start_date is None:
            self._settings['datalogger']['start_date'] = time.time()

    def __setup_tinydb(self):

        self.__db = TinyDB('datalogger.json')

    def __setup_sqlite3(self):

        """Create and connect to a memory SQLITE3 database
        """

        self.__db_connection = sqlite3.connect(':memory:')
        self.__logger.info('Connect to SQLITE3 database')
        create_datalogger_table = f'CREATE TABLE IF NOT EXISTS {self.__table_name} (id INTEGER PRIMARY KEY, timestamp REAL NOT NULL, elapsed REAL NOT NULL)'
        cursor = self.__db_connection.cursor()
        cursor.execute(create_datalogger_table)

        for name, value in flatten(self.datalogger_current).items():
            cursor.execute(f'ALTER TABLE {self.__table_name} ADD COLUMN {name} TEXT')

        self.__logger.info('Complete SQLITE3 database setup')

    def __add_multiple(self, data: dict = {}):

        """Add multiple values to the database
        :param data: A dictionary with the data to store. The keys correspond to the column names.
        :type data: dict, optional
        """

        # Do nothing if datalogger is disabled
        if not self.datalogger_active:
            self.__logger.error('Datalogger is already running')
            return

        self.__index += 1
        now = time.time()
        started = self._settings['datalogger']['start_date']
        keys = ['timestamp', 'elapsed']
        values = [f"'{val}'" for val in [now, now - started]]

        for key, value in flatten(data).items():
            key = str(key if key is not None else '')
            value = str(value if value is not None else '')
            keys.append(key)
            values.append("'" + value + "'")

        keys_formatted = ', '.join(keys)
        values_formatted = ', '.join(values)
        cursor = self.__db_connection.cursor()
        sql = f'INSERT INTO {self.__table_name} ({keys_formatted}) VALUES ({values_formatted})'
        cursor.execute(sql)

    def __close(self, export_data: bool = True):

        """Close the database connection
        :param export_data: Export all data to CSV before clearing and closing the database. Default is ``True``
        :type export_data: bool, optional.
        """

        if not self.datalogger_active:
            self.__logger.error('Close failed: datalogger is not running')
            return  # Do nothing if datalogger is disabled

        if self.datalogger_backend == 'tinydb':
            self.__db.truncate()
            self.__db.close()
        elif self.datalogger_backend == 'sqlite3':
            if export_data:
                self.__export_to_csv()
            cursor = self.__db_connection.cursor()
            cursor.execute(f'DROP TABLE {self.__table_name}')
            self.__logger.info(f'Drop SQLITE3 table "{self.__table_name}"')
            self.__db_connection.close()
            self.__logger.info('Close SQLITE3 database connection')

        self.__is_running.clear()
        self.__start_date = None
        self.__stop_date = None
        self.__stop_count = None

    def __export_to_csv(self, delimiter: str = ";", clear_database: bool = True):

        """Export all recorded data to a csv file
        :param delimiter: Delimiter for the csv file. Default is ``;``
        :type delimiter: str, optional
        :param clear_database: Delete all entries in the database after export. Default is ``True``
        :type clear_database: bool, optional
        The csv file holds all recorded values since the start or the last export of the datalogger.
        Files are stored in ``.__files`` as ``DataLoggerFile`` object.
        """

        if not self.datalogger_active:
            self.__logger.error('Export failed: datalogger is not running')
            return

        filename = f'{self.__table_name}_{int(time.time())}.csv'
        file = os.path.join(self.data_dir, filename)
        self.__logger.info(f'Write {self.__table_name} to {filename}')

        if self.datalogger_backend == 'sqlite3':
            cursor = self.__db_connection.cursor()
            cursor.execute(f'SELECT * from {self.__table_name}')
            new_file = DataLoggerFile(name=filename, records=self.__index)

            with io.StringIO() as csv_stream:
                csv_writer = csv.writer(csv_stream, delimiter=delimiter)
                csv_writer.writerow([i[0] for i in cursor.description])
                csv_writer.writerows(cursor)
                new_file.data = csv_stream.getvalue()

            self.__files[new_file.name] = new_file

            if clear_database:
                self.__dump_event.clear()
                cursor.execute(f'DELETE from {self.__table_name}')
                self.__logger.info(f'Clear SQLITE3 table "{self.__table_name}"')
                self.__index = 0

    @property
    def __start_date(self):

        return self._settings['datalogger']['start_date']

    @__start_date.setter
    def __start_date(self, value):

        self.__set_start_date(value)

    def __set_start_date(self, new_date=None):

        """Start the datalogger with a specific time delay
        """

        if new_date == self.__start_date:
            return  # Nothing to do

        if new_date is None:
            self._settings['datalogger']['start_date'] = None
            self.__logger.info('Deactive automatic start time for datalogger')
            return True

        if new_date < time.time():
            self.__logger.error('Start time for datalogger must be in the future')
            return False

        if self.__stop_date is not None:
            if self.__stop_date < new_date:
                self.__logger.error('Start time for the datalogger must be before stop time')
                return False

        self._settings['datalogger']['start_date'] = new_date

        return True

    @property
    def __stop_date(self):

        return self._settings['datalogger']['stop_date']

    @__stop_date.setter
    def __stop_date(self, value):

        self.__set_stop_date(value)

    def __set_stop_date(self, new_date=None):

        """Limit the duration the datalogger should store values
        """

        if new_date == self.__stop_date:
            return  # Nothing to do

        if new_date is None:
            self._settings['datalogger']['stop_date'] = None
            self.__logger.info('Deactive time limit for datalogger')
            return True

        if new_date < time.time():
            self.__logger.error('Time limit for datalogger must be in the future')
            return False

        if self.__start_date is not None:
            if self.__start_date > new_date:
                self.__logger.error('Stop time for the datalogger must be after start time')
                return False

        self._settings['datalogger']['stop_date'] = new_date

        return True

    @property
    def __stop_count(self) -> int:

        return self._settings['datalogger']['stop_count']

    @__stop_count.setter
    def __stop_count(self, value: int):

        self.__set_stop_count(value)

    def __set_stop_count(self, new_count: int):

        """Limit the number of entries to be recorded in the datalogger
        :param new_count: The numbe of entries after which the datalogger should stop
        :type new_count: int
        """

        if new_count == self.__stop_count:
            return  # Nothing to do

        if new_count is None:
            self._settings['datalogger']['stop_count'] = None
            self.__logger.info('Deactive entry limit for datalogger')
            return True

        try:
            new_count = int(new_count)
        except ValueError:
            self.__logger.info('Entry limit for datalogger must be an integer')
            return False

        if new_count <= self.__index:
            self.__logger.error(f'Entry limit for datalogger must be larger than the current amount of entries ({self.__index})')
            return False

        self._settings['datalogger']['stop_count'] = new_count

    def datalogger_collect(self):

        pass

    print("Hello World")
