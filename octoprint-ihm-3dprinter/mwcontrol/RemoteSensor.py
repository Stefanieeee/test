# coding=utf-8
import time
from .BaseController import BaseController
from .BaseConnectionHandler import BaseConnectionHandler
from typing import Union
import json

"""定义了一些可用属性
"""

class RemoteSensor(BaseConnectionHandler, BaseController):

    """Base class for sensors

    """

    def __init__(self, *args, **kwargs):

        """Class constructor

        """

        super().__init__(*args, **kwargs)
        self.__value = None
        self.__last_update = 0
        self.__timeseries = []
        self.__logger = self.logger.getChild('RemoteSensor')
        self.__settings = RemoteSensor.get_defaults()
        self.__out_of_range = False

    @classmethod
    def get_defaults(cls) -> dict:

        """Get the default values for this class

        :return: The default values
        :rtype: dict

        """

        return {
            'name': 'default',
            'timeout': 2.0,
            'fallback': None,
            'minimum': None,
            'maximum': None,
            'offset': 0.0,
            'coefficient': 1.0,
            'mavg_time_length': 0.5
        }

    def update_settings(self, settings: dict = None, *args, **kwargs) -> None:

        """Update the settings for this instance

        *Allowed settings*
        - name: The name of the sensor. Default is ``default``
        - timeout: Data timeout. The sensor will be considered unavailable if the last received
            data is older than the time ``timeout`` in seconds from now. Default is ``1.0`` seconds.
        - fallback: Fallback value for unvailable sensor. Returned if sensor is unavailable
        - minimum: Minimum value. If set, the sensor will clamp received values to this minimum. If
            the minimum is it, ``out_of_range`` becomes ``True``. Default is ``None`` (deactivated)
        - maximum: Maximum value. Similar to minimum.
        - offset: Offset value. This value is added to each received value. Default is ``0.0``
        - coefficient: Coefficient value. This value is multiplied with the recived value before
            before adding the offset. Default is ``1.0``.
        - mavg_time_length: Moving average time length. Default time period to selecting recorded
            values for the moving average. Default is ``0.5``.

        .. note::
            The ``out_of_range`` flag is set for minimum and maximum without distinction.

        .. note::
            Miniums cannot be larger or equal to maximums and vice versa and settings such values
            will be ignored.

        """

        super().update_settings(settings=settings, *args, **kwargs)
        # Create the settings variables and fill it with defaults
        if getattr(self, '__settings', None) is None:
            self.__settings = RemoteSensor.get_defaults()
            settings = self.__settings.copy()

        if settings is None:
            return

        # Set the individual variables and properties
        for attr in ['minimum', 'maximum', 'timeout', 'fallback', 'offset', 'coefficient', 'name']:
            if attr in settings:
                setattr(self, attr, settings[attr])

    @property
    def status(self) -> dict:

        """Get the current status of this sensors

        :return: Status data for this sensor
        :rtype: dict
        """

        data = super().status
        data.update(self.__settings)
        data['value'] = self.value
        data['available'] = 1 if self.available else 0
        data['out_of_range'] = 1 if self.out_of_range else 0

        return data

    @property
    def available(self) -> bool:

        """Check if the sensors is available

        :getter: returns ``False`` if the module did not recieve new data for a time period longer
            than defined in ``timeout``.

        """

        if time.time() - self.__last_update >= self.__settings['timeout']:
            return False

        return True

    @property
    def is_available(self):

        self.__logger.warning('.is_available is deprecated. Please use .available')

        return self.available

    @property
    def out_of_range(self) -> bool:

        """Check if the current values are out of the defined range.

        .. note::
            Ranges can be set with ``.minimum`` and ``.maximum``

        """

        return self.__out_of_range

    @property
    def value(self) -> Union[float, None]:

        """Control the value of the sensor

        :getter: Return the last received value
        :setter: Set a new value

        .. note::
            If the sensor is not available the fallback value will be return instead.

        """

        if self.available:
            return self.__value

        return self.fallback

    @value.setter
    def value(self, value: float):

        try:
            value = float(value)
        except ValueError:
            self.__logger.error('Value cannot be parsed as float')
            return
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')
            return

        value = self.offset + value * self.coefficient

        if self.minimum is not None and value < self.minimum:
            value = max(value, self.minimum or value)
            self.__out_of_range = True

        elif self.maximum is not None and value > self.maximum:
            value = min(value, self.maximum or value)
            self.__out_of_range = True

        else:
            self.__out_of_range = False

        self.__value = value
        self.__last_update = time.time()

        if len(self.__timeseries) > 120:
            _ = self.__timeseries.pop(0)

        self.__timeseries.append((self.__last_update, self.__value))

    @property
    def name(self) -> str:

        """The name of the current sensor

        :getter: Return the current name
        :setter: Set the new name

        """

        return self.__settings['name']

    @name.setter
    def name(self, value: str):

        if isinstance(value, str):
            self.__settings['name'] = value
        else:
            self.__logger.error('Sensor name must be a str.')

    @property
    def timeout(self) -> float:

        """Sensor timeout after which the sensor is considered unvailable

        :getter: Get the current timeout.
        :setter: Set a new timeout.

        """

        return self.__settings['timeout']

    @timeout.setter
    def timeout(self, value: float):

        try:
            self.__settings['timeout'] = float(value)
        except ValueError:
            self.__logger.error(f'Timeout "{value}" cannot be parsed as float')
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')

    @property
    def fallback(self):

        """Value returned if the sensor is unavailable

        :getter: Return the current fallback value
        :setter: Set a new fallback value
        """

        return self.__settings['fallback']

    @fallback.setter
    def fallback(self, value: Union[float, None]):

        if value is None:
            self.__settings['fallback'] = None
            return

        try:
            self.__settings['fallback'] = float(value)
        except ValueError:
            self.__logger.error('Fallback value must be float or None')
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')

    @property
    def offset(self) -> float:

        """Offset to be applied to each value

        :getter: Return the current offset
        :setter: Set a new offset

        """

        return self.__settings['offset']

    @offset.setter
    def offset(self, value):

        try:
            self.__settings['offset'] = float(value)
        except ValueError:
            self.__logger.error('Offset must be a float')
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')

    @property
    def coefficient(self):

        """Coefficient to be applied for each value

        :getter: Return the current coefficient
        :setter: Set a new coefficient

        """

        return self.__settings['coefficient']

    @coefficient.setter
    def coefficient(self, value):

        try:
            self.__settings['coefficient'] = float(value)
        except ValueError:
            self.__logger.error('Coefficient must be a float')
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')

    @property
    def minimum(self) -> Union[float, None]:

        """Minimum value that is considered valid

        :getter: Return the current minimum value.
        :setter: Set a new minimum value. Set to ``None`` to disable.
        """

        return self.__settings['minimum']

    @minimum.setter
    def minimum(self, value: Union[float, None]):

        if value is None:
            self.__settings['minimum'] = None
            return

        try:
            value = float(value)
        except ValueError:
            # self.__settings['minimum'] = None
            self.__logger.error('Failed to parse minimum value as float')
            self.__logger.debug(f'Minimum is not changed, remains at: {self.minimum}')
            return
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')
            return

        if (self.maximum is not None) and (value >= self.maximum):
            self.__logger.error('Minimum cannot be larger or equal to maximum')
        else:
            self.__settings['minimum'] = value

    @property
    def maximum(self) -> Union[float, None]:

        """ Maximum value that is considered valid

        :getter: Return the current maximum value.
        :setter: Set a new mayimum value. Set to ``None`` to disable.
        :type: float/NoneType
        """

        return self.__settings['maximum']

    @maximum.setter
    def maximum(self, value: Union[float, None]):

        if value is None:
            self.__settings['maximum'] = None
            return

        try:
            value = float(value)
        except ValueError:
            # self.__settings['maximum'] = None
            self.__logger.error('Failed to parse maximum value as float')
            self.__logger.debug(f'Maximum is not changed, remains at: {self.maximum}')
            return
        except Exception as e:  # This should never happen but if it does, let us know.
            self.__logger.error(f'Exception: {e}')
            return

        if (self.minimum is not None) and (value <= self.minimum):
            self.__logger.error('Maximum cannot be inferior or equal than minimum')
        else:
            self.__settings['maximum'] = value

    def get_moving_sum(self, delta: float = None) -> float:

        """Calculate the sum of all values within a specific time span from now

        :param delta: The duration from now in seconds.
        :type delta: float, optional

        """

        if not self.available:
            return self.fallback, 0

        delta = delta or self.__settings['mavg_time_length']
        now = time.time()
        filtered_values = [v for d, v in self.__timeseries if now - d < delta]

        if len(filtered_values) == 0:  # Does this actually happend with available == True?
            return self.__value, 0

        return sum(filtered_values), len(filtered_values)

    def get_moving_average(self, delta: float = None) -> float:

        """Calculate the mocing average of all values within a specific time span from now

        :param delta: The duration from now in seconds.
        :type delta: float, optional

        """

        delta = delta or self.__settings['mavg_time_length']
        values_sum, values_length = self.get_moving_sum(delta)

        return values_sum if values_length == 0 else values_sum/values_length

    def datalogger_collect(self):

        super().datalogger_collect()


"""
"""


class MicrowavePowerSensor(RemoteSensor):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.name = 'microwave_power'
        self.__logger = self.logger.getChild('MicrowavePowerSensor')
        self.__data = {
            'FWD_AVG': 0.0,
            'REV_AVG': 0.0,
            'PEAK_ENV': 0.0
        }

    def on_message(self, message: str, encoding: str = 'utf-8') -> None:

        """Callback for processing incomming messages from a sensor

        :param message: The message string as received from the sensor
        :type message: str
        :param encoding: The encoding to be used for the message string. Default: ``utf-8``
        :type encoding: str, optional
        """

        try:
            self.__data = json.loads(message.decode(encoding))
        except Exception as e:
            self.__logger.error(e)
        else:
            self.__last_update = time.time()

    def datalogger_collect(self):

        super().datalogger_collect()
        self.datalogger_current.update(self.__data)
        self.datalogger_current['available'] = 1 if self.available else 0




"""TemperatureSensor
"""




class TemperatureSensor(RemoteSensor):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.name = 'temperature'
        self.__logger = self.logger.getChild('FLIRTemperatureSensor')
        self.maximum = 250
        self.message_key = 'TEMP'

    def on_message(self, message: str, encoding: str = 'utf-8') -> None:

        """Callback for processing incomming messages from a sensor

        :param message: The message string as received from the sensor
        :type message: str
        :param encoding: The encoding to be used for the message string. Default: ``utf-8``
        :type encoding: str, optional
        """

        message = message.decode(encoding).split(' ')

        if (len(message) == 2) and (message[0] == self.message_key):
            self.value = message[1]

    def datalogger_collect(self):

        super().datalogger_collect()
        self.datalogger_current.update(self.status)

    @property
    def value(self):

        """Get an averaged value instead of the last value

        :getter: Return the moving average from the last 0.5s
        :setter: Identical to parent setter.
        """

        return self.get_moving_average(0.5)

    @value.setter
    def value(self, value):

        super(TemperatureSensor, self.__class__).value.fset(self, value)


class FilamentSensor(RemoteSensor):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.name = 'filament'
        self.__last_step_update = 0.0
        self.__logger = self.logger.getChild('FilamentSensor')
        self.coefficient = 3.3
        self.message_key = 'STEP'

    def on_message(self, message, encoding='utf-8'):

        message = message.decode(encoding).split(' ')

        if (len(message) == 2) and (message[0] == self.message_key):
            self.setSteps(message[1])

    def datalogger_collect(self):

        super().datalogger_collect()
        self.datalogger_current.update(self.status)

    def setSteps(self, count: float):

        """Calculate the filament speed based on the number of steps

        """

        try:
            count = float(count)
        except ValueError:
            return

        now = time.time()
        delta = now - self.__last_step_update
        # Calculate the steps per time (seconds)
        if 0 < delta < self.timeout:
            self.value = count/delta

        self.__last_step_update = now

    @property
    def status(self) -> dict:

        """Extend the status data with speed information.

        """

        status = super().status
        status['speed'] = self.speed

        return status

    @property
    def speed(self):

        """Get an averaged value of the speed

        :getter: Return the moving average from the last 0.5s
        """

        return self.get_moving_average(0.5)


class VirtualFilamentSensor(RemoteSensor):

    """Virtual filament sensor

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__logger = self.logger.getChild('VirtualFilamentSensor')
        self.__speed = 0

    def datalogger_collect(self):

        super().datalogger_collect()
        self.datalogger_current.update({
            'speed': self.speed,
            'available': 1 if self.available else 0
        })

    @property
    def speed(self):

        return self.__speed

    @speed.setter
    def speed(self, value):

        self.__speed = value

class PyrometerTemperatureSensor(RemoteSensor):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__name = 'pyrometer'
        self.__logger = self.logger.getChild('PyrometerTemperatureSensor')
        self.coefficient = 0.01
        self.offset = 2.5
        self.message_key = 'PYRO'

    def on_message(self, message, encoding='utf-8'):

        message = message.decode(encoding).split(' ')

        if (len(message) == 2) and (message[0] == self.message_key):
            self.value = message[1]

    def datalogger_collect(self):

        super().datalogger_collect()
        self.datalogger_current.update(self.status)

    @property
    def temperature(self):

        return self.get_moving_average(0.5)


class RemoteSensorSimulator(BaseConnectionHandler, BaseController):

    pass


class RemoteTemperatureSensorSimulator(RemoteSensorSimulator):

    pass


class RemoteFilamentSensorSimulator(RemoteSensorSimulator):

    pass
