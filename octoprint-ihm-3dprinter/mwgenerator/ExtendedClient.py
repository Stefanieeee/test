from .Client import Client
import math

"""扩展客户端
   添加了最大值最小值功能 防止设备损坏
"""

def check_available(rvalue=None):

    def decorator(target_function):

        def wrapper(self, *args, **kwargs):

            if self.available:

                return target_function(self, *args, **kwargs)

            return lambda self, *args, **kwargs: rvalue

        return wrapper

    return decorator


class PWMMixin:

    @property
    def pwm_power_min(self):

        """Get the minium PWM power output

        :getter: Return the min PWM power output.
        :type: float
        """

        if self.ready:
            return float(self.power*self.pwm_min)

        return None

    @pwm_power_min.setter
    def pwm_power_min(self, value):

        self._settings['pwm_power_min'] = float(value)

    @property
    def pwm_power_max(self):

        """Get the maximum PWM power output

        :getter: Return the maximum PWM power output.
        :type: float
        """

        if self.ready:
            return float(self.power*self.pwm_max)

        return None

    @pwm_power_max.setter
    def pwm_power_max(self, value):

        self._settings['pwm_power_max'] = float(value)

    @property
    def pwm_power(self):

        """Get the current PWM power.

        :getter: Return the current PWM power.
        :type: float
        """

        if self.ready:
            return float(self.power*self.pwm)

        return None

    @pwm_power.setter
    def pwm_power(self, value):

        try:
            value = float(value)
        except ValueError:
            self.logger.error(f'Could not read the PWM power {value}')
            return

        value = min(value, self.pwm_power_max)
        value = max(value, self.pwm_power_min)
        available_power = self.power

        if available_power > 0:
            self.pwm = value / available_power

    @property
    def pwm_period(self):

        return self._settings['pwm_period']['current']

    @pwm_period.setter
    def pwm_period(self, value):

        try:
            value = float(value)
        except ValueError:
            self.logger.error(f'Value {value} cannot be parsed as float for pwm_period')
        except TypeError:
            self.logger.error(f'{type(value)} is not allowed for pwm_period')
        else:
            value = max(value, self.pwm_period_minimum)
            value = max(value, self.pwm_period_maximum)
            self._settings['pwm_period']['current'] = value

    @property
    def pwm_period_minimum(self):

        return self.ontime_min + self.offtime_minimum

    @pwm_period_minimum.setter
    def pwm_period_minimum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: pwm_period_minimum')

    @property
    def pwm_period_maximum(self):

        return self.ontime_max + self.offtime_maximum

    @pwm_period_maximum.setter
    def pwm_period_maximum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: pwm_period_maximum')

    @property
    def pwm(self):

        """Get the current pulse width

        :getter: Return the current pulse width ratio (ontime to total cycle time)
        :setter: Set an arbitrary puls width ratio. This will adapt :attr:`ExtendedClient.ontime`
            accordingly
        :type: float
        """

        return self.ontime/self.pwm_period

    @pwm.setter
    def pwm(self, value):

        try:
            value = float(value)
        except ValueError:
            value = -1
        value = max(value, self.pwm_min)
        value = min(value, self.pwm_max)
        self.ontime = value * self.pwm_period

    @property
    def pwm_max(self):

        """Get the maximum possible pusle to cycle time ratio

        :getter: Return the maximum for :attr:`ExtendedClient.pwm` which depends on
            :attr:`ExtendedClient.ontime_max`
        :type: float
        """

        ontime_max = min(self.ontime_max, self.pwm_period - self.offtime_minimum)
        return ontime_max / self.pwm_period

    @property
    def pwm_min(self):

        """Get the minimum possible pulse to cycle time ratio
        :getter: Return the minimum for :attr:`ExtendedClient.pwm` which depends on :attr:`ExtendedClient.ontime_min`
        :type: float
        """

        ontime_min = max(self.ontime_min, self.pwm_period - self.offtime_maximum)
        return ontime_min / self.pwm_period

    def set_pwm_lin(self, value):

        if not self.ready:
            return

        try:
            value = float(value)
        except ValueError:
            value = -1

        if (0 <= value <= 1):
            self.pwm = value*(self.pwm_max-self.pwm_min) + self.pwm_min


class TimingMixin:

    @property
    def ontime(self):

        """Get the PWM ontime in *Nanoseconds [ns]*.

        :getter: Return :attr:`Client.ontime <hpg.Client.Client.ontime>`.
        :setter: Set :attr:`Client.ontime <hpg.Client.Client.ontime>` after checking limits.
        :type: int

        **Examples**

        .. code-block:: python
           :linenos:
           :caption: Simple example

           Client.ontime = 10000  # Set the power 10.000ns

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.ontime_min = 10000
            >>> ExtendedClient.ontime_max = 100000
            >>> ExtendedClient.ontime = 5000  # Ignored becasue of .ontime_min
            >>> ExtendedClient.ontime
            10000
            >>> ExtendedClient.ontime = 500000  # Ignored becasue of .ontime_max
            >>> ExtendedClient.ontime
            100000

        """

        return super().ontime

    @ontime.setter
    def ontime(self, value):

        if value is None:
            return

        try:
            value = float(value)
        except ValueError:
            value = -1

        if value < 0:
            raise ValueError

        value = max(value, self.ontime_min)  # Disabled if ontime_min == None
        value = min(value, self.ontime_max)  # Disabled if ontime_max == None
        super(ExtendedClient, self.__class__).ontime.fset(self, value)
        super(ExtendedClient, self.__class__).offtime.fset(self, self.pwm_period - value)

    @property
    def ontime_min(self):

        """Get the minimum PWM ontime allowed in *Nanoseconds [ns]*.

        :getter: Set the minimum PWM ontime in *Nanoseconds [ns]*. Must be larger or equal to 0 and
            smaller or equal to :attr:`ExtendedClient.ontime_max`.
        :setter: Return ``0`` or the minimum PWM ontime in *Nanoseconds [ns]* as float.
        :type: float, None

        **Examples**

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.ontime_min = 15000
            >>> ExtendedClient.ontime = 10000
            >>> ExtendedClient.ontime
            15000

        .. note::
            The minimum PWM ontime limit is disabled if set to ``None``
            (default value). If :attr:`ExtendedClient.ontime_max` is
            set, the minimum PWM ontime cannot be larger and will be
            limited to :attr:`ExtendedClient.ontime_max`.
        """

        return max(self._settings['ontime']['minimum'], self.pwm_period - self.offtime_maximum)

    @ontime_min.setter
    def ontime_min(self, value):

        try:
            value = float(value) if value is not None else -1
        except ValueError:
            value = -1

        if value <= 0:
            value = ExtendedClient.get_defaults()['ontime']['minimum']
            self.logger.info(f'Reset minimum ontime to default: {value}ns')
        else:
            value = min(value, ExtendedClient.get_defaults()['ontime']['maximum'])
            value = max(value, ExtendedClient.get_defaults()['ontime']['minimum'])
            self.logger.info(f'Set minimum ontime to {value}ns')

        self._settings['ontime']['minimum'] = value
        self.ontime = self.ontime_min if self.ontime is None else self.ontime

    @property
    def ontime_max(self):

        """Get the maximum PWM ontime allowed in *Nanoseconds [ns]*.

        :getter: Return the maximum PWM ontime in *Nanoseconds [ns]* as float.
        :setter: Set the maximum PWM ontime in *Nanoseconds [ns]*. Must be larger or equal to
            :attr:`ExtendedClient.ontime_min`.
        :type: float

        **Examples**

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.ontime_max = 1000000
            >>> ExtendedClient.ontime = 1500000
            >>> ExtendedClient.ontime
            1000000

        .. note::
            The maximum PWM ontime limit is disabled if set to ``None``
            (default value). The getter then returns
            :attr:`ExtendedClient.offtime`.

        .. important::
            If :attr:`ExtendedClient.ontime_min` is set, the maximum
            PWM ontime cannot be smaller and will be limited to
            :attr:`ExtendedClient.ontime_min`.
        """

        return min(self._settings['ontime']['maximum'], self.pwm_period - self.offtime_minimum)

    @ontime_max.setter
    def ontime_max(self, value):

        try:
            value = float(value) if value is not None else -1
        except ValueError:
            value = -1

        if value <= 0:
            value = ExtendedClient.get_defaults()['ontime']['maximum']
            self.logger.info(f'Reset maximum ontime to default value {value}ns')
        else:
            value = max(value, ExtendedClient.get_defaults()['ontime']['minimum'])  # ontime_max >= ontime_min
            value = min(value, ExtendedClient.get_defaults()['ontime']['maximum'])  # ontime_max <= offtime
            self.logger.info(f'Set maximum ontime to {value}ns')

        self._settings['ontime']['maximum'] = value
        self.ontime = self.ontime

    @property
    def offtime(self):

        """Get the PWM offtime in *Nanoseconds [ns]*.

        :getter: Return :attr:`Client.offtime <hpg.Client.Client.offtime>`.
        :setter: Set :attr:`Client.offtime <hpg.Client.Client.offtime>`. Must be larger or equal to
            :attr:`ExtendedClient.ontime_max`.
        :type: int

        **Examples**

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.ontime_max = 100000
            >>> ExtendedClient.offtime = 500000
            >>> ExtendedClient.offimte
            100000

        .. important::
            If :attr:`ExtendedClient.ontime_max` is set, the
            PWM offtime cannot be smaller and will be limited to
            :attr:`ExtendedClient.ontime_max`.
        """

        return super().offtime

    @offtime.setter
    def offtime(self, value):

        try:
            value = float(value)
        except ValueError:
            value = -1

        if value <= 0:
            self.logger.warning('Error processing offtime. Nothing is changed')
            # raise ValueError
        else:
            value = max(value, ExtendedClient.get_defaults()['ontime']['minimum'])  # offtime >= ontime_max
            value = min(value, ExtendedClient.get_defaults()['ontime']['maximum'])  # offtime >= ontime
            super(ExtendedClient, self.__class__).offtime.fset(self, value)

    @property
    def offtime_maximum(self):

        return self._settings['offtime']['maximum']

    @offtime_maximum.setter
    def offtime_maximum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: offtime_maximum')

    @property
    def offtime_minimum(self):

        return self._settings['ontime']['minimum']

    @offtime_minimum.setter
    def offtime_minimum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: offtime_minimum')


class PowerMixin:

    @property
    def power(self):

        """Get the output power in *Watts [W]*.

        :getter: Return :attr:`Client.power <hpg.Client.Client.power>` and multiplies it with
            :attr:`ExtendedClient.power_step`.
        :setter: Set :attr:`Client.power <hpg.Client.Client.power>` after dividing it (without rest)
            by :attr:`ExtendedClient.power_step`.
        :type: float

        **Examples**

        .. code-block:: python
           :linenos:
           :caption: Simple example

           Client.power = 10.0  # Set the power to 10.0W

        .. code-block:: python
            :linenos:
            :caption: Example with power_step

            >>> Client.power_step = 5.0
            >>> Client.power = 11.2
            >>> Client.power
            10.0

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.power_min = 2.0
            >>> ExtendedClient.power_max = 12.0
            >>> ExtendedClient.power = 1.0
            >>> ExtendedClient.power
            2.0
            >>> ExtendedClient.power = 13.0
            >>> ExtendedClient.power
            12.00

        .. warning::
            Power must be set in in multiples of :attr:`ExtendedClient.power_step`.
            Otherwise the value is rounded to the next lower step as shown in the examples.

        """

        power = super().power

        if power is not None:
            return power*(self.power_step or 1)

        return None

    @power.setter
    def power(self, value):

        try:
            value = float(value) if value is not None else 0.0
        except ValueError:
            raise ValueError(value)

        value = max(value, 0.0)                           # Power cannot be negative
        value = min(value, self.power_max or value)     # Power must be below maximum if set
        value = max(value, self.power_min or value)     # Power must be above minimum if set

        if self.power_step is not None:
            value = math.ceil(value/self.power_step)    # Get the next power step if set

        if value == 0.0 and self.power_min is not None and self.power_step > self.power_min > 0.0:
            value = self.power_step

        super(ExtendedClient, self.__class__).power.fset(self, value)

        if self.active:
            super(ExtendedClient, self.__class__).rf.fset(self, 1)

    @property
    def power_min(self):

        """Get the minimum output power allowed in *Watts [W]*.

        :getter: Set the minimum power in *Watts [W]*.
        :setter: Return None or the minimum power in *Watts [W]* as float.
        :type: float, None

        **Examples**

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.power_min = 5.0
            >>> ExtendedClient.power = 1.0
            >>> ExtendedClient.power
            5.0

        .. important::
            :attr:`ExtendedClient.power_min` must be larger or equal to ``0`` and
            smaller or equal to :attr:`ExtendedClient.power_max` if set. Larger
            values are set so :attr:`ExtendedClient.power_max` without any notification
            or exception.

        .. note::
            Setting :attr:`ExtendedClient.power_min` to ``None`` disables the limit.
        """

        return float(self._settings['power']['minimum'] or 0)

    @power_min.setter
    def power_min(self, value):

        try:
            value = float(value) if value is not None else -1
        except ValueError:
            value = -1

        value = max(value, 0.0)
        value = min(value, self.power_max or value)

        if self.power_step > value > 0:
            value = self.power_step

        self.logger.info(f'Set minimal power to {value}W')
        self._settings['power']['minimum'] = value

    @property
    def power_max(self):

        """Get the maximum output power allowed in *Watts [W]*.

        :getter: Set the maximum output power in *Watts [W]*.
        :setter: Return None or the maximum output power in *Watts [W]* as float.
        :type: float, None

        **Examples**

        .. code-block:: python
            :linenos:
            :caption: Example with limits

            >>> ExtendedClient.power_max = 5.0
            >>> ExtendedClient.power = 7.0
            >>> ExtendedClient.power
            5.0

        .. important::
            :attr:`ExtendedClient.power_max` must be larger or equal
            to :attr:`ExtendedClient.power_min` if set. Smaller
            values are set so :attr:`ExtendedClient.power_min`
            without any notification or exception.

        .. note::
            Setting :attr:`ExtendedClient.power_max` to ``None`` disables the limit.
        """

        return float(self._settings['power']['maximum'] or 0)

    @power_max.setter
    def power_max(self, value):

        """Set the maximum power the source should deliver while operating.

        The maximum power must be equal to or bigger than the minimum power.
        Lower values are capped at minimum power or 0.
        """

        try:
            value = float(value) if value is not None else -1
        except ValueError:
            value = -1

        value = max(value, self.power_min or value)

        if self.power_step:
            value = math.ceil(value/self.power_step)*self.power_step

        self.logger.info(f'Set maximum power to {value}W')
        self._settings['power']['maximum'] = value

    @property
    def power_step(self):

        """Get the step size for the power setting.

        Some device, like the HPG Microwave source, only allow output
        power setting in dicrete steps. By enablding this features,
        :class:`ExtendedClient` will include this requirement into
        all power calculations and settings. Steps are disabled by default.

        See :attr:`ExtendedClient.power` for examples.

        :getter: Get the power step size in *Watts [W]*.
        :setter: Set the power step size in *Watts [W]*. Set *None* to disable.
        :type: float, None
        """

        return self._settings['power']['step']

    @power_step.setter
    def power_step(self, value):

        try:
            value = float(value) if value is not None else 0

        except ValueError:
            value = 0

        value = max(value, 0)
        self.logger.debug(f'Set RF power step to {value}W')
        self._settings['power']['step'] = value


class SensorMixin:

    @property
    def temperature_max(self):

        """Get the maximum allowed operation temperature

        :getter: Return the maximum allowed operation temperature
        :setter: Set the maximum allowed operation temperature
        :type: float/NoneType
        """

        return self._settings['temperature']['maximum']

    @temperature_max.setter
    def temperature_max(self, value):

        if value is not None:

            try:
                value = float(value)
            except ValueError:
                raise ValueError

        if value != self._settings['temperature']['maximum']:
            self._settings['temperature']['maximum'] = value
            self.logger.info(f'Set maximum temperature to {value}')

    @property
    def temperature_min(self):

        """Get the minimum allowed operation temperature

        :getter: Return the minimum allowed operation temperature
        :setter: Set the minimum allowed operation temperature
        :type: float/NoneType
        """

        return self._settings['temperature']['minimum']

    @temperature_min.setter
    def temperature_min(self, value):

        if value is not None:

            try:
                value = float(value)
            except ValueError:
                raise ValueError

        if value != self._settings['temperature']['minimum']:
            self._settings['temperature']['minimum'] = value
            self.logger.info(f'Set minimum temperature to {value}')


class ExtendedClient(SensorMixin, PowerMixin, TimingMixin, PWMMixin, Client):

    """Extends the Client base class

    The :class:`Client <hpg.Client.Client>` class only implements
    the communication with the device as well as the basic commands.
    The :class:`ExtendedClient` class additionally implements many features.

    :param logger: Use an existing logger to attached the child logger.. Default is `False`.
    :type client: class:`logging.Logger`
    :param settings: A dictionary holding all settings to be updated. Default is ``None``.
    :type settigs: dict, optional

    .. note::
        For some values a minimum or maximum value can be set. Setting
        a value out of this limits will not cause any error or
        exception but the value will be limited to to respective minimum
        or maximum. Limits can be disabled by setting them to ``None``.
    """

    def __init__(self, logger=False, settings=None, *args, **kwargs):

        """Class constructor
        """

        super().__init__(logger=logger, settings=settings)
        self.datalogger_current = {}

    @classmethod
    def get_defaults(cls):

        """Get the default Settings vor all values managed by :class:`ExtendedClient`

        :return: The default settings of this class.
        :rtype: dict
        """

        defaults = Client.get_defaults()

        defaults['ontime'].update({
            'minimum': 1e4,  # From datasheet
            'maximum': 1e7  # From datasheet
        })

        defaults['offtime'].update({
            'minimum': 1e4,
            'maximum': 1e8
        })

        defaults['power'].update({
            'minimum': 10,
            'maximum': 100,
            'step': 10
        })

        defaults['temperature'] = {
            'maximum': None,
            'minimum': None
        }

        defaults['pwm_power'] = {
            'minimum': None,
            'current': None,
            'maximum': None
        }

        defaults['active'] = False
        defaults['fixed_pwm_value'] = 'OFFTIME'
        defaults['pwm_period'] = {
            'minimum': None,
            'current': 2e5,
            'maximum': None
        }
        return defaults

    @property
    def ready(self):

        if not super().ready:
            return False

        for attr in ['ontime_min', 'ontime_max', 'offtime_minimum', 'offtime_maximum']:
            if not getattr(self, attr, False):
                self.logger.info(f'Attribute {attr} is not set!')
                return False

        return True

    @property
    def active(self):

        return all((self.check_thermal_protection(), bool(self._settings['active'])))

    @active.setter
    def active(self, value):

        value = all((self.check_thermal_protection(), bool(value)))

        if not value:
            super(ExtendedClient, self.__class__).rf.fset(self, 0)

        self._settings['active'] = value

    @property
    def rf(self):

        return super().rf

    @rf.setter
    def rf(self, value):

        if not self.active:
            return

        super(ExtendedClient, self.__class__).rf.fset(self, 1 if bool(value) else 0)

    @property
    def frequency_maximum(self):

        # return self._settings['frequency']['maximum']
        return None

    @frequency_maximum.setter
    def frequency_maximum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: frequency_maximum')

    @property
    def frequency_minimum(self):

        # eturn self._settings['frequency_minimum']['minimum']
        return None

    @frequency_minimum.setter
    def frequency_minimum(self, value):

        # raise NotImplementedError
        self.logger.error('NotImplementedError: frequency_minimum')

    def datalogger_collect(self):

        self.datalogger_current.update({
            'host': str(self.host)
            # Mode?
        })

        power = [
            'power',
            'power_minimum',
            'power_maximum',
            'power_step',
            'power_forward',
            'power_reflected'
        ]
        timings = [
            'ontime',
            'offtime',
            'ontime_min',
            'ontime_max',
            'offtime_minimum',
            'offtime_maximum']
        pwm = [
            'pwm_power_min',
            'pwm_power_max',
            'pwm_min',
            'pwm_max',
            'pwm_power',
            'pwm_period',
            'pwm_period_minimum',
            'pwm_period_maximum'
        ]
        temperature = [
            'temperature_minimum',
            'temperature_maximum',
            'temperature']
        status = [
            'rf',
            'active',
            'available',
            'port',
            'frequency',
            'frequency_minimum',
            'frequency_maximum'
            'ready',
            'mode'
        ]

        for key in power + timings + pwm + temperature + status:
            self.datalogger_current.update({key: getattr(self, key, None)})

        if len(self.datalogger_current):
            super(ExtendedClient, self.__class__).caching.fset(self, True)

    def update_settings(self, settings=None):

        """Update the settings.

        :attr settings: A dictionary holding all settings to update.
        :type settings: dict, optional

        .. note::
            See :meth:`ExtendedClient.getDefaults()` and
            :meth:`Client.getDefaults` for valid structures.
        """

        self._settings = getattr(self, '_settings', ExtendedClient.get_defaults())

        if settings is None:
            return

        Client.update_settings(self, settings)

    @check_available(False)
    def check_thermal_protection(self):

        """ TODO
        """

        if self.rf == 0:
            return True

        check_maximum, check_minimum = True, True

        if self.temperature_max is not None:
            check_maximum = self.temperature < self.temperature_max

        if self.temperature_min is not None:
            check_minimum = self.temperature > self.temperature_min

        if not all((check_minimum, check_maximum)):
            self.logger.critical(f'Device temperature is above limit ({self.temperature_max}°C)!')
            self.logger.critical(f'Thermal shutdown at {self.temperature}°C')
            return False

        return True
