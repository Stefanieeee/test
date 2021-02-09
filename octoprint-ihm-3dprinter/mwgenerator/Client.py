# coding=utf-8

import socket
import logging
import time
from tinydb import TinyDB


"""客户端连接
   引入了一个缓存系统 复制各个状态的值
   不断检查缓存值，如果超过某个值，就刷新整个缓存
"""

def check_lock(target_function):

    def wrapper(self, *args, **kwargs):

        if self.locked:
            self.logger.error('Device is locked!')

            return lambda self, *args, **kwargs: None

        return target_function(self, *args, **kwargs)

    return wrapper


def check_available(target_function):

    def wrapper(self, *args, **kwargs):

        if not self.available:
            self.logger.error('Device is not available!')

            return lambda self, *args, **kwargs: None

        return target_function(self, *args, **kwargs)

    return wrapper


class Client(object):

    """Client library for controlling a HPG Microwave source

    :param logger: Use an existing logger to attached the child logger.
    :type client: class:`logging.Logger`
    :param settings: A dictionary holding all settings to be updated. Defaults to ``None``
    :type settigs: dict, optional
    """

    def __init__(self, *args, **kwargs):

        """Class constructor
        """
        self._configure_logger()
        self.update_settings()
        self.__is_available = False
        self.__is_locked = False
        self._presets = TinyDB('presets.json')
        self.__is_available_last = 0
        self.__cache_age = 0
        self.__reconnect_time = 0

    @classmethod
    def get_defaults(cls):

        """Return the default class values as a dict

        :return: A dict holding all class default values
        :rtype: dict

        .. note::
            The structure of the return dict is identitcal to the
            dict structure necessary in :meth:`Client.updateSettings()`.
        """

        return {
            'connection': {
                'host': '192.168.0.111',
                'port': 5025,
                'delay': 0.01
            },
            'mode': 'PWM',
            'frequency': {
                'current': 245000
            },
            'power': {
                'current': 1
            },
            'rf': 0,
            'ontime': {
                'current': 10000
            },
            'offtime': {
                'current': 1000000
            },
            'loglevel': 'DEBUG',
            'cache': False,
            'id': None,
            'serial': None,
            'version': None
        }

    def update_settings(self, settings=None):

        """Overwrite the local settings with new values and update internal components

        :param settings: A dictionary holding all settings to be updated. Default is ``{}``
        :type settigs: dict, optional

        **Example 1**

        .. code-block:: python
           :linenos:

           # Update device IP
           settings = {'connection': {'ip': '192.168.0.1'}}
           Client.updateSettings(settings)

        **Example 2**

        .. code-block:: python
           :linenos:

           # Update device port and frequency
           settings= {'connection': {'port': 1234}, 'frequency': 245000}
           Client.updateSettings(settings)

        .. note::
            The dict in ``settings`` has the same structure than the
            dict returned by ``.getDefaults``

        """

        self._settings = getattr(self, '_settings', Client.get_defaults())

        if settings is None:
            return False

        for key in ['rf', 'frequency', 'mode']:
            self._settings[key] = settings.get(key, self._settings[key])

        for key in ['power', 'ontime', 'offtime']:
            self._settings[key].update(settings.get(key, {}))

        if 'port' in settings.get('connection', {}):
            self.port = int(self._settings['connection']['port'])

        if 'host' in settings.get('connection', {}):
            self.host = self._settings['connection']['host']

    @property
    def ready(self):

        if not self.available:
            return False

        for attr in ['ontime', 'offtime', 'frequency', 'power', 'mode']:
            if getattr(self, attr, None) is None:
                self.logger.info(f'Attribute {attr} is not set!')
                return False

        return True

    def preset_save(self, id=None, name=None):

        settings = {}
        settings.update(self._settings)
        settings['_preset_name'] = str(name)

        for key in ['connection', 'id', 'version', 'serial', 'loglevel']:
            del settings[key]

        if id is None:
            id = self._presets.insert(settings)
            self.logger.info(f'Create new preset with ID {id}')
        else:
            self._presets.update(self._settings, doc_ids=[id])
            self.logger.info(f'Update preset {id}')

        return id

    def preset_delete(self, id):

        try:
            self._presets.remove(doc_ids=[id])
        except KeyError:
            self.logger.error(f'Could not delete preset {id}')
        else:
            self.logger.info(f'Delete preset {id}')

    def preset_list(self, show_in_log=False):

        all_presets = self._presets.all()

        if len(all_presets) == 0:
            self.logger.info('No presets in database')

        if show_in_log:
            for entry in all_presets:
                id, name = entry.doc_id, entry['_preset_name']
                self.logger.info(f'{id} - {name}')

        return all_presets

    @check_lock
    def preset_load(self, id):

        settings = self._presets.get(doc_id=id)

        if settings is not None:
            self.update_settings(settings=settings)
            self.apply()
            self.logger.info(f'Load preset {id}')
        else:
            self.logger.error('Could not find preset {id}')

    @check_lock
    def apply(self, safe_mode=True):

        if not self.available:  # Abort if device is not available
            return
        # Abort if at least one attribute is not set

        for attr in ['mode', 'rf', 'frequency', 'ontime', 'offtime', 'power']:
            if getattr(self, attr, None) is None:
                return

        for key in ['mode', 'rf', 'frequency']:
            setattr(self, key, self._settings[key])

        for key in ['ontime', 'offtime', 'power']:
            setattr(self, key, self._settings[key]['current'])

        self.logger.info('Apply settings to device')

    # @check_available
    def __load_from_device(self):

        """Load values form device

        This method loads all values from the device and checks them against the values
        stored in the cache. If the values differ the values are updated.
        """

        # self.getIDN()
        if not self.__is_available:
            return

        previous_cache_state = self.caching
        self.caching = False

        cached_power = self._settings['power']['current']
        current_power = self.power
        if cached_power is not None and current_power is not None:
            if getattr(self, 'power_step', None) is not None:
                cached_power *= self.power_step or 1
            if cached_power != current_power:
                self.logger.warning(f'Generator changed power from {cached_power} to {current_power}')


        cached_mode = self._settings['mode']
        current_mode = self.mode
        if cached_mode is not None and current_mode is not None:
            if cached_mode != current_mode:
                self.logger.warning(f'Generator changed mode from {cached_mode} to {current_mode}')
                self.mode = cached_mode

        cached_offtime = self._settings['offtime']['current']
        current_offtime = self.offtime
        if current_offtime is not None and cached_offtime is not None:
            if cached_offtime != current_offtime:
                self.logger.warning(f'Generate changed offtime from {cached_offtime} to {current_offtime}')
                self.offtime = cached_offtime

        cached_ontime = self._settings['ontime']['current']
        current_ontime = self.ontime
        if current_ontime is not None and cached_ontime is not None:
            if cached_ontime != current_ontime:
                self.logger.warning(f'Generate changed ontime from {cached_ontime} to {current_ontime}')
                self.ontime = cached_ontime

        cached_frequency = self._settings['frequency']
        current_frequency = self.frequency
        if current_frequency is not None and cached_frequency is not None:
            if cached_frequency != current_frequency:
                self.logger.warning(f'Generator changed frequency from {cached_frequency} to {current_frequency}')
                self.frequency = cached_frequency

        self.caching = previous_cache_state

    def lock(self):

        self.logger.info('Lock device')
        self.__is_locked = True

    def unlock(self):

        self.logger.info('Unlock device')
        self.__is_locked = False

    @property
    def locked(self):

        return self.__is_locked

    def _configure_logger(self, name=None, level=None, parent=None):

        """Get child of a given logger or setup standalone default logger

        :param logger: Use an existing logger to attached the child logger.
        :type client: class:`logging.Logger`
        :param name: Set a specific name for the child logger. Defaults to ``__class__.__name__``
        :type name: str, optional
        :param level: Set the loglevel for the child logger. Defaults to ``__class__.LOGLEVEL``
        :type level: str, optional
        """

        level = 'DEBUG' if level is None else level
        name = self.__class__.__name__ if name is None else name

        if parent is None:
            self.logger = logging.getLogger(name)
        else:
            self.logger = logging.getLogger(parent).getChild(name)

        self.logger.setLevel(getattr(logging, level))

    def __connect(self, timeout=0.5):

        """Connect a socket.

        :param timeout: Set the socket timeout in seconds. Defauls to ``1``.
        :type timeout: int, optional
        """

        time.sleep(self._settings['connection']['delay'])

        # if self.__reconnect_time > time.time():
        #     return

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(timeout)
        except socket.error as msg:
            self.logger.error('Failed to create and connect. \
                Error code: {}, Error message: {}'.format(*msg))
            raise DeviceNotAvailable
        except Exception as e:
            self.logger.error(f'Socket exception: {e}')
            raise DeviceNotAvailable
        else:
            host = str(self.host)

            try:
                self.s.connect((host, self.port))
            except socket.timeout:
                self.logger.error(f'Timeout while connecting to {host}:{self.port}')
                raise DeviceNotAvailable
            except socket.error:
                self.logger.error(f'Error connecting to {host}:{self.port}')
                raise DeviceNotAvailable
            else:
                # self.available = True
                self.logger.debug(f'Connected to {host}:{self.port}')

    def __disconnect(self):

        """Close the socket.
        """

        self.s.close()

    def __set_command(self, cmd, encoding='utf-8'):

        """Send a command and do not wait for a response

        :param cmd: Command to send
        :type cmd: str
        :param encoding: Encode the command with this encoding. Defaults to `utf-8`.
        :type encoding: str, optional
        """

        try:
            self.__connect()
        except DeviceNotAvailable:
            self.available = False
            return
        else:
            self.available = True

        device_available = False

        try:
            self.s.sendall(f'{cmd}\r\n'.encode(encoding))
        except socket.timeout:
            self.logger.error(f'SET-Timeout while connecting to {self.host}:{self.port}')
            raise DeviceNotAvailable
        except socket.error:
            self.logger.error(f'Error connecting to {self.host}:{self.port}')
            raise DeviceNotAvailable
        else:
            device_available = True
            self.logger.debug(f'Send "{cmd}"')

        self.available = device_available
        self.__disconnect()

    def __get_command(self, cmd, encoding='utf-8', buffer_length=4096):

        """Send a query and wait for a response.

        :param cmd: Command to send
        :type cmd: str
        :param encoding: Encode the command and decode the response with this encoding. Defaults to
            `utf-8`
        :type encoding: str, optional
        :param buffer_length: Socket receive buffer length in bytes.
        :type buffer_length: int, optional
        """

        try:
            self.__connect()
        except DeviceNotAvailable:
            self.available = False
            raise DeviceNotAvailable
        else:
            self.available = True

        response = None

        try:
            self.s.sendall('{}\r\n'.format(cmd).encode(encoding))
            self.logger.debug('Send "{}"'.format(cmd))
        except socket.timeout:
            self.logger.error(f'GET-Timeout while connecting to {self.host}:{self.port}')
        except socket.error:
            self.logger.error(f'Error connecting to {self.host}:{self.port}')
        else:

            try:
                response = self.s.recv(buffer_length).decode(encoding).rstrip('\r\n')
                self.logger.debug(f'Receive "{response}"')
            except socket.timeout:
                self.logger.error(f'Timeout while connecting to {self.host}:{self.port}')
            except socket.error:
                self.logger.error(f'Error connecting to {self.host}:{self.port}')

        self.__disconnect()

        if response is not None:
            self.available = True
            return response

        self.available = False
        raise DeviceNotAvailable

    @property
    def host(self):

        return self._settings['connection']['host']

    @host.setter
    def host(self, value):

        self._settings['connection']['host'] = value
        self.__is_available_last = 0
        self.__cache_age = 0

    @property
    def port(self):

        return self._settings['connection']['port']

    @port.setter
    def port(self, value):

        self._settings['connection']['port'] = value
        self.__is_available_last = 0
        self.__cache_age = 0

    @property
    def caching(self):

        return self._settings['cache']

    @caching.setter
    def caching(self, value):

        self._settings['cache'] = bool(value)

    @property
    def serial(self):

        return self._settings['serial']

    @serial.setter
    def serial(self, value):

        self._settings['serial'] = value

    @property
    def id(self):

        return self._settings['id']

    @id.setter
    def id(self, value):

        self._settings['id'] = value

    @property
    def version(self):

        return self._settings['version']

    @version.setter
    def version(self, value):

        self._settings['version'] = value

    @property
    def mode(self):

        """Get the operation mode.

        :getter: Return the operation mode. Returns the cached value if caching is enabled.
        :setter: Set a new operation mode and save it in the settings. The value is only applied if
            it differs from the actual setting.
        :type: str

        **Example**

        .. code-block:: python
           :linenos:

           Client.mode = 'CW'  # Set the mode to CW

        .. note::
            Valid operation modes are `CW`, `PWM`, `NWA` and
            `PWM-NWA`. All other values are ignored.
        """

        cached_mode = self._settings['mode']

        if self.caching and self._settings['mode'] is not None:
            return cached_mode

        try:
            self._settings['mode'] = self.__get_command('CONF:MOD?').replace('"', '')
        except ValueError:
            self.logger.error('Received mode was faulty. Set default')
            self.frequency = Client.get_defaults()['mode']
        except DeviceNotAvailable:
            self.logger.error('Could not read mode')
            self._settings['mode'] = None  # Client.MODE
            return None

        return self._settings['mode']

    @mode.setter
    @check_lock
    def mode(self, value):

        """Only set the mode if `value` is set to a valid operation
        mode and if `value` differs from the current setting.
        """

        try:
            value = str(value)
        except ValueError:
            raise ValueError

        if value not in ['CW', 'PWM', 'NWA', 'NWA-PWM']:
            raise UnkownCommandException(f'Unknown command {value}')

        if value == self._settings['mode'] and self.caching:
            return

        try:
            self.__set_command(f'CONF:MOD {value}')
        except DeviceNotAvailable:
            self.logger.warning('Could not set mode')
        else:
            self.logger.info(f'Set mode to {value}')
            self._settings['mode'] = value

    @property
    def frequency(self):

        """Get the output frequency in multiples of 10kHz.

        :getter: Return the operation frequency. Returns the cached value if caching is enabled.
        :setter: Set a new operation frequency and save it in the settings. The value is only
            applied if it differs from the actual setting.
        :type: int
        :raises: ValueError

        **Example**

        .. code-block:: python
           :linenos:

           Client.frequency = 245000  # Set the frequency to 2,45GHz

        .. note::
            The operating frequency is returned and set in multiples
            of 10kHz. It is not checked wether ``value`` fullfills
            this requirement or the limits from the devices datasheet.
        """

        cached_frequency = self._settings['frequency']

        if self.caching and cached_frequency is not None:
            return cached_frequency

        try:
            self._settings['frequency'] = int(self.__get_command('CONF:FREQ?'))
        except ValueError:
            self.logger.error('Received frequency was faulty. Set default')
            self.frequency = Client.get_defaults()['frequency']
        except DeviceNotAvailable:
            self._settings['frequency'] = None
            self.logger.error('Could not read frequency')
            return None

        return self._settings['frequency']

    @frequency.setter
    @check_lock
    def frequency(self, value):
        """Only set frequency if `value` differs from the current setting.
        """

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Frequency must be positive and integer')

        if value == self._settings['frequency'] and self.caching:  # Only set if value is different or query
            return

        try:
            self.__set_command(f'CONF:FREQ {value}')
        except DeviceNotAvailable:
            self.logger.warning('Could not set frequency')
        else:
            self.logger.info(f'Set frequency to {value}')
            self._settings['frequency'] = value

    @property
    def fsweep_frequency_start(self):

        """The first frequency of the frequency sweep

        :getter: Return the start frequency of the sweep in multiples of 10KHz.
        :setter: Set the start frequency of thr sweep in multiples of 10KHz.
        :type: float
        """

        return float(self.__get_command('CONFigure:FSWEEp:FSTART?'))

    @fsweep_frequency_start.setter
    def fsweep_frequency_start(self, value):

        if self.__is_locked:
            return

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Frequency must be positive and integer')
        else:
            self.__set_command('CONFigure:FSWEEp:FSTART {}'.format(value))

    @property
    def fsweep_frequency_step(self):

        """The frequency step of the frequency sweep

        :getter: Return the frequency step of the sweep in multiples of 10KHz.
        :setter: Set the frequency step of thr sweep in multiples of 10KHz.
        :type: float
        """

        return float(self.__get_command('CONFigure:FSWEEp:FSTEP?'))

    @fsweep_frequency_step.setter
    def fsweep_frequency_step(self, value):

        if self.__is_locked:
            return

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Frequency must be positive and integer')
        else:
            self.__set_command('CONFigure:FSWEEp:FSTEP {}'.format(value))

    @property
    def fsweep_frequency_stop(self):

        """The last frequency of the frequency sweep

        :getter: Return the last frequency of the sweep in multiples of 10KHz.
        :setter: Set the last frequency of thr sweep in multiples of 10KHz.
        :type: float
        """

        return float(self.__get_command('CONFigure:FSWEEp:FSTOP?'))

    @fsweep_frequency_stop.setter
    def fsweep_frequency_stop(self, value):

        if self.__is_locked:
            return

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Frequency must be positive and integer')
        else:
            self.__set_command('CONFigure:FSWEEp:FSTOP {}'.format(value))

    def fsweep_start(self):

        """Start the frequency sweep.

        .. note::
            The frequency sweep will only start if there is no other frequency sweep
            or sequence running on the device.
        """

        if self.fsweep_status:
            self.logger.error('A frequency sweep is already running.')
        elif self.sequence_status:
            self.logger.error('A sequence is already running.')
        else:
            self.logger.info('Start the frequency sweep')
            self.__set_command('CONTrol:FSWEEp:START')

    @property
    def fsweep_status(self):

        """Query if a frequency sweep is already running

        :getter: Check if a frequency sweep is currently running on the device
        :type: bool
        """

        return bool(self.__get_command('CONTrol:FSWEEp:STATus?'))

    @property
    def sequence_status(self):

        """Query if a sequence is already running

        :getter: Check if a sequence is currently running on the device
        :type: bool
        """

        return bool(self.__get_command('CONTrol:SEQuence:STATus?'))

    def fsweep_stop(self):

        """Stop the frequency sweep.

        """

        self.logger.info('Stop the frequency sweep')
        self.__set_command('CONTrol:FSWEEp:STOP')

    @property
    def power(self):

        """Get the output power in multiples of 10W.

        :getter: Return the output power. Returns the cached value if caching is enabled.
        :setter: Set a new output power and save it in the settings. The value is only applied if it
            differs from the actual setting.
        :type: int

        **Example**

        .. code-block:: python
           :linenos:

           Client.power = 2  # Set the output power to 20W

        .. note::
            The output power is returned and set in multiples
            of 10W. It is not checked wether ``value`` fullfills
            this requirement or the limits from the devices datasheet.
        """

        if self.caching and self._settings['power']['current'] is not None:
            return self._settings['power']['current']

        try:
            self._settings['power']['current'] = float(self.__get_command('CONF:POW?'))
        except ValueError:
            self.logger.error('Received power was faulty. Set default')
            self.power = Client.get_defaults()['power']['current']
        except DeviceNotAvailable:
            self.logger.warning('Device not available, could not read power.')
            self._settings['power']['current'] = None
            return None

        return self._settings['power']['current']

    @power.setter
    @check_lock
    def power(self, value):

        """Only set power if `value` differs from the current setting.
        """

        try:
            value = float(value)
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Power must be positive and int')

        if value == self._settings['power']['current'] and self.caching:
            return

        try:
            self.__set_command(f'CONF:POW {value}')  # Only set if value is different or query
        except DeviceNotAvailable:
            self.logger.warning('Device not available, could not set power.')
            self.available = False
        else:
            self.logger.info(f'Set power to {value}W')
            self._settings['power']['current'] = value

    @property
    def rf(self):

        """Get the rf output state.

        :getter: Return the output state. Returns the cached value if caching is enabled.
        :setter: Set a new output state and save it in the settings. Set ``0`` for `Off` and ``1``
            for `On`. The value is only applied if it differs from the actual setting.
        :type: int

        **Example**

        .. code-block:: python
           :linenos:

           Client.rf = 1  # Enable the RF output

        """

        if self.caching and self._settings['rf'] is not None:
            return self._settings['rf']

        try:
            self._settings['rf'] = int(self.__get_command('CONT:RF?'))
        except DeviceNotAvailable:
            self.logger.warning('Device not available, could not read RF state.')
            self._settings['rf'] = None
            return None
        except ValueError:
            self.logger.error('Received RF state was faulty. Disable RF')
            self.rf = 0

        return self._settings['rf']

    @rf.setter
    @check_lock
    def rf(self, value):
        """Only set rf if `value` differs from the current setting.
        """

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value not in [0, 1]:
            raise ValueError('RF must be 0 or 1')

        if value == self._settings['rf'] and self.caching:  # Only set if value is different or query
            return

        try:
            self.__set_command(f'CONT:RF {value}')
        except DeviceNotAvailable:
            self.logger.warning('Device not available, could not set RF state.')
            self.available = False
        else:
            self.logger.info(f'Set RF to {value}')
            self._settings['rf'] = value

    @property
    def ontime(self):

        """Get the PWM ontime in ns.

        :getter: Return the ontime. Returns the cached value if caching is enabled.
        :setter: Set the ontime in ns. The value is only applied if it differs from the actual
            setting.
        :type: int

        **Example**

        .. code-block:: python
           :linenos:

           Client.ontime = 10000 # Set the PWM ontime to 10µs
        """

        cached_ontime = self._settings['ontime']['current']
        default_ontime = Client.get_defaults()['ontime']['current']

        if self.caching and cached_ontime is not None:
            return cached_ontime

        try:
            self._settings['ontime']['current'] = int(self.__get_command('CONF:PWM:ON?'))
        except ValueError:
            self.logger.error('Received ontime was faulty. Set default')
            self.ontime = default_ontime
        except DeviceNotAvailable:
            self._settings['ontime']['current'] = None
            self.logger.error('Could not read ontime')
            return None

        return self._settings['ontime']['current']

    @ontime.setter
    @check_lock
    def ontime(self, value):
        """Only set ontime if `value` differs from the current setting.
        """

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Ontime must be positive and int')
        elif value == self._settings['ontime']['current'] and self.caching:
            return

        try:
            self.__set_command(f'CONF:PWM:ON {value}')
        except DeviceNotAvailable:
            self.available = False
            self.logger.error('Could not set ontime')
        else:
            self.logger.info(f'Set ontime to {value}ns')
            self._settings['ontime']['current'] = value

    @property
    def offtime(self):

        """Get the PWM offtime in ns.

        :getter: Return the offtime. Returns the cached value if caching is enabled.
        :setter: Set the offitime in ns. The value is only applied if it differs from the actual
            setting.
        :type: int

        **Example**

        .. code-block:: python
           :linenos:

           Client.offtime = 10000 # Set the PWM offtime to 10µs
        """

        cached_offtime = self._settings['offtime']['current']
        default_offtime = Client.get_defaults()['offtime']['current']

        if self.caching and cached_offtime is not None:
            return cached_offtime

        try:
            self._settings['offtime']['current'] = int(self.__get_command('CONF:PWM:OFF?'))
        except ValueError:
            self.logger.error('Received offtime was faulty. Set default')
            self.offtime = default_offtime
        except DeviceNotAvailable:
            self._settings['offtime']['current'] = None
            self.logger.error('Could not read offtime')
            return None

        return self._settings['offtime']['current']

    @offtime.setter
    @check_lock
    def offtime(self, value):

        """Only set offtime if `value` differs from the current
        setting.
        """

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError('Offtime must be positive and integer')
        elif value == self._settings['offtime']['current'] and self.caching:
            # Do nothing if caching is enabled and value not changed
            return

        try:
            self.__set_command(f'CONF:PWM:OFF {value}')
        except DeviceNotAvailable:
            self.logger.error('Could not set offtime')
        else:
            self.logger.info(f'Set offtime to {value}ns')
            self._settings['offtime']['current'] = value

    @property
    def temperature(self):

        """Fetch and return the current temperature in °C from the
        device.

        :return: Temperature in °C.
        :rtype: float

        .. note::
            The HPG device has several temperature sensors. This one
            is located is located next to the circulator and load.
        """

        if not getattr(self, '_last_update_temperature', False):
            self._last_update_temperature = 0

        if time.time() - self._last_update_temperature > 1:

            try:
                self._temperature = float(self.__get_command('SENSe:TEMPerature?'))
            except DeviceNotAvailable:
                return None
            except ValueError:
                self.logger.error('Could not read temperature')
                return None
            else:
                self._last_update_temperature = time.time()

        return self._temperature

    @property
    def power_forward(self):

        """Fetch and return the measured forward power in Watt [W] from the device

        :return: Forward power in Watt [W]
        :rtype: float

        .. note::
            These values are not very accurate. You may use them for getting a
            ballpark figure but you'll need to add an external measurement
            for more precise values.
        """

        if not getattr(self, '_last_update_power_forward', False):
            self._last_update_power_forward = 0

        if time.time() - self._last_update_power_forward > 1:

            try:
                self._power_forward = float(self.__get_command('SENSe:POWer:FORward?'))
            except DeviceNotAvailable:
                return None
            except ValueError:
                self.logger.error('Could not read forward power')
                return None
            else:
                self._last_update_power_forward = time.time()

        return self._power_forward

    @property
    def power_reflected(self):

        """Fetch and return the measured reflected power in Watt [W] from the device

        :return: Forward power in Watt [W]
        :rtype: float

        .. note::
            These values are not very accurate. You may use them for getting a
            ballpark figure but you'll need to add an external measurement
            for more precise values.
        """

        if not getattr(self, '_last_update_power_reflected', False):
            self._last_update_power_reflected = 0

        if time.time() - self._last_update_power_reflected > 1:

            try:
                self._power_reflected = float(self.__get_command('SENSe:POWer:REFLect?'))
            except DeviceNotAvailable:
                return None
            except ValueError:
                self.logger.error('Could not read reflected power')
                return None
            else:
                self._last_update_power_reflected = time.time()

        return self._power_reflected

    def getIDN(self):

        """Fetch ID, serial and version number from the device and
        save it in the settings.
        """

        result = self.__get_command('*IDN?').split(',')

        try:
            self.id = result[1][1:]
            self.serial = result[2]
            self.version = result[3]
            self.logger.debug(f'Device ID {self.id}, Serial {self.serial}, Version {self.version}')
        except IndexError:
            self.logger.error('Could not read IDN')

    @property
    def available(self):

        """Check if the device is available

        """

        now = time.time()

        if now - self.__is_available_last > 1.0:

            try:
                self.getIDN()
            except DeviceNotAvailable:
                self.available = False
            else:
                self.available = True
                self.__is_available_last = time.time()

        if self.__is_available:

            if now - self.__cache_age > 5.0:
                self.__load_from_device()
                self.logger.info('Reload microwave generator cache')
                self.__cache_age = time.time()

        return self.__is_available

    @available.setter
    def available(self, value):

        if value:
            self.__is_available = True
            self.__is_available_last = time.time()
        else:
            self.__is_available = False
            self.__is_available_last = 0
            self.__cache_age = 0

    @property
    def is_available(self):

        return self.available

class ExceptionBaseClass(Exception):

    def __init__(self, *args, **kwargs):

        self.message = args[0] if args else None
        self.logger = kwargs.get('logger', False)


    def __str__(self):

        if self.message:
            return 'Exception: {}'.format(self.message)

        return 'Exception raised. No message available'


class DeviceNotAvailable(ExceptionBaseClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.logger:
            self.logger.warning('Device is not available.')


class UnkownCommandException(ExceptionBaseClass):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        if self.logger:
            self.logger.warning('Unkown command.')
