# coding=utf-8

import flask
from flask_socketio import SocketIO, send
import threading
from .DataLoggerMixin import DataLoggerMixin
from .LoggerMixin import LoggerMixin
from tinydb import TinyDB

"""Flask 搭建Web框架
"""
class WebServerMixin(LoggerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flask_configure(autostart=kwargs.get('flask_autostart', False))

    def _flask_configure(self, autostart=True):
        self._flask = flask.Flask(__name__)
        self._flask_socketio = SocketIO(self._flask)
        if autostart:
            self.flask_start()
        self._flask_route_add()

    def flask_start(self, daemon=True, port=20000):
        self._flask_thread = threading.Thread(target=self._flask.run, kwargs={'port': port})
        self._flask_thread.setDaemon(daemon)
        self._flask_thread.start()
        self.logger.info('Start flask thread')

    def _flask_route_add(self):

        @self._flask_socketio.on('message')
        def ping(message):
            if message == 'ping':
                send('pong')

        @self._flask.route('/')
        def _flask_root():
            return 'OK'


class CheckValueMixin:
    def check_temperature(self, value, clamp=False):
        """Check if the temperature is valid

        :param value: Input temperature value
        :type value: int, float, str
        :param clamp: clamp the value to the absolute minimum
        :return: Temperature value if correct
        :rtype: float
        :raises: ValueError, TypeError
        """

        minimums = {'K': 0, 'C': -273.15, 'F': -459.670}

        minimum = minimums[self.unit_temperature]

        try:

            return self._value_check_minimum(value, minimum, clamp, exclusive=False)

        except CheckValueException:

            raise CheckTemperatureError

    def _value_check_interval(self, value, span=(None, None), clamp=(False, False), exclusive=(False, False)):
        """Check if the value is contained inside an interval

        :param value: The value
        :type value: int, float
        :param span: An interval as tuple. Default is ``(None, None)``
        :type span: tuple, optional
        :param clamp: Control if value should be clamped at interval border. Default is ``(False, False)``
        :type clamp: tuple, optional
        :param exlusive: Control if interval border is exclusive. Default is ``(False, False)``
        :type exclusive: tuple, optional
        :return: The value after checks
        :rtype: float
        :raises: ArgumentException, CheckValueException
        """

        if span == (None, None):
            return value

        if not all(isinstance(x, (float, int, type(None))) for x in span):
            raise ArgumentException('Elements of span must be int, float or None')

        if not all(isinstance(x, bool) for x in clamp + exclusive):
            raise ArgumentException('Elements of clamp and exclusive must be boolean')

        if not all((((span[0] or span[1]) <= span[1]), (span[1] or (span[0] >= span[0])))):
            raise ArgumentException('Minimum is above maximum.')

        if span[0] is not None:
            value = self._value_check_minimum(value, span[0], clamp[0], exclusive[0])

        if span[1] is not None:
            value = self._value_check_maximum(value, span[1], clamp[1], exclusive[1])

        return value

    def _value_check_minimum(self, value, minimum=None, clamp=False, exclusive=False):

        if minimum is None:
            return value

        if value > minimum:
            return value

        elif (value == minimum and not exclusive) or (value < minimum and clamp):
            return max(value, minimum)

        raise CheckValueException

    def _value_check_maximum(self, value, maximum=None, clamp=False, exclusive=False):

        if maximum is None:
            return value

        if value < maximum:
            return value

        elif (value == maximum and not exclusive) or (value > maximum and clamp):
            return min(value, maximum)

        raise CheckValueException


class BaseController(DataLoggerMixin, WebServerMixin, CheckValueMixin, LoggerMixin):

    def __init__(self, data_dir='.', *args, **kwargs):

        self._presets = TinyDB('presets.json')
        self.data_dir = data_dir
        super().__init__(*args, **kwargs)
        self.update_settings(settings=kwargs.get('settings', None))
        self.logger.debug('Initialize BaseController class')

    @classmethod
    def get_defaults(cls):

        """Return the default values of this class as as dict

        :return: Default settings as dict
        :rtype: dict

        """

        return {
            'units': {'temperature': 'C'}
        }

    def update_settings(self, settings=None, *args, **kwargs):

        """Update the settings if needed

        :param settings: New settings to apply
        :type settings: dict, optional
        """

        self._settings = getattr(self, '_settings', BaseController.get_defaults())
        super().update_settings(settings=settings, *args, **kwargs)

        if settings is None:
            return

        self.unit_temperature = settings.get('units', {}).get('temperature', self.unit_temperature)

    # def preset_save(self, id=None, name=None):
        # settings = {}
        # settings.update(self._settings)
        # settings['_preset_name'] = str(name)
        # for key in ['connection', 'id', 'version', 'serial', 'loglevel']:
        #     del settings[key]
        # if id is None:
        #     id = self._presets.insert(settings)
        #     self.logger.info(f'Create new preset with ID {id}')
        # else:
        #     self._presets.update(self._settings, doc_ids=[id])
        #     self.logger.info(f'Update preset {id}')
        # return id
    #     pass
    #
    # def preset_delete(self, id):
    #     try:
    #         self._presets.remove(doc_ids=[id])
    #     except KeyError:
    #         self.logger.error(f'Could not delete preset {id}')
    #     else:
    #         self.logger.info(f'Delete preset {id}')
    #
    # def preset_list(self, show_in_log=False):
    #     all_presets = self._presets.all()
    #     if len(all_presets) == 0:
    #         self.logger.info('No presets in database')
    #     if show_in_log:
    #         for entry in all_presets:
    #             id, name = entry.doc_id, entry['_preset_name']
    #             self.logger.info(f'{id} - {name}')
    #     return all_presets

    @property
    def unit_distance(self):

        return 'C'

    @unit_distance.setter
    def unit_distance(self, value):

        if value in ['mm', 'inch']:
            self.logger.warning(f'System is now using {value} as distance unit')

    @property
    def unit_speed(self):

        return 'mm/s'

    @unit_speed.setter
    def unit_speed(self, value):

        pass

    @property
    def unit_temperature(self):

        return self._settings['units']['temperature']

    @unit_temperature.setter
    def unit_temperature(self, value):

        if value in ['C', 'K', 'F']:
            self._settings['units']['temperature'] = value
            self.logger.warning(f'System is now using {value} as temperature unit')

        else:

            try:
                self.logger.warning(f'{value} is not a valid unit')

            except AttributeError:  # Logger is not set
                pass


class CheckValueException(Exception):
    pass


class CheckTemperatureError(CheckValueException):
    pass


class ArgumentException(Exception):
    pass
