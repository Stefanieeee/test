# coding=utf-8
import logging
from simple_pid import PID
from .BaseController import BaseController
from typing import Union

"""PID算法数值
"""

class PIDMixin(BaseController):

    def __init__(self, *args, **kwargs):

        """Constructor method.
        """

        self.pid = PID()
        super().__init__(*args, **kwargs)
        self.update_settings(settings=kwargs.get('settings', {}))
        self.__slow_mode = False
        self.__logger = logging.getLogger('MCS.PID')

    @classmethod
    def get_defaults(cls) -> dict:

        """Return the default class values.

        :return: A dict holding all class default values
        :rtype: dict
        """

        return {
            'tunings': {
                'Kp': 1.0,          # PID Parameter P
                'Ki': 0,            # PID Parameter I
                'Kd': 0,            # PID Parameter D
            },
            'output': {
                'minimum': 0,       # Minimum PID output value
                'current': 0,
                'maximum': 100      # Maximum PID output value
            },
            'setpoint': {
                'minimum': 0,       # Minimum setpoint value
                'current': 0,
                'maximum': None     # Maximum setpoint value
            },
            'sample_time': 0.1
        }

    def update_settings(self, settings: dict = {}):

        """Internal method to update the PID settings

        The only reason fo this method was to improve code readbility because
        :meth:`ExtendedClient.updateSettings()` got a little big.

        :param settings: A dictionary holding all settings to be updated.
        :type settings: dict
        """

        super().update_settings(settings=settings)

        if 'pid' not in self._settings:
            self._settings['pid'] = PIDMixin.get_defaults()
            settings = self._settings

        pid_settings = settings.get('pid', None)

        if pid_settings is None:
            return

        for key, value in pid_settings.get('tunings', {}).items():
            if key in ['Kp', 'Ki', 'Kd']:
                setattr(self, key, value)

        if 'minimum' in pid_settings.get('output', {}):
            self.pid_control_min = pid_settings['output']['minimum']

        if 'maximum' in pid_settings.get('output', {}):
            self.pid_control_max = pid_settings['output']['maximum']

        if 'setpoint' in pid_settings:
            self.pid_target = pid_settings['setpoint'].get('current', self.pid_target)
            self.pid_target_minimum = pid_settings['setpoint'].get('minimum', self.pid_target_minimum)
            self.pid_target_maximum = pid_settings['setpoint'].get('maximum', self.pid_target_maximum)

        self.pid_sample_time = pid_settings.get('sample_time', self.pid_sample_time)

    def __set_slow_mode(self, state: bool = True):

        """Temporarly set different PID values

        """

        if state and not self.__slow_mode:
            self.__slow_mode = True
            self.__previous_Kp = self.Kp
            self.Kp = 0.1
            self.logger.getChild('PID').info('Enable slow mode!')

        if not state and self.__slow_mode:
            self.__slow_mode = False
            self.Kp = self.__previous_Kp
            self.logger.getChild('PID').info('Disable slow mode!')

    @property
    def Kp(self) -> float:

        """PID P parameter

        :getter: Return the current parameter P
        :setter: Set the new parameter P and reset the PID control

        """

        return self.pid.Kp

    @Kp.setter
    def Kp(self, value: float):

        try:
            value = float(value)
        except ValueError:
            pass
        else:
            self._settings['pid']['tunings']['Kp'] = value
            self.pid.Kp = value
            self.pid.reset()

    @property
    def Ki(self) -> float:

        """PID I parameter

        :getter: Return the current parameter I
        :setter: Set the new parameter I and reset the PID control

        """

        return self.pid.Ki

    @Ki.setter
    def Ki(self, value: float):

        try:
            value = float(value)
        except ValueError:
            pass
        else:
            self._settings['pid']['tunings']['Ki'] = value
            self.pid.Ki = value
            self.pid.reset()

    @property
    def Kd(self) -> float:

        """PID D parameter

        :getter: Return the current parameter D
        :setter: Set the new parameter D and reset the PID control

        """

        return self.pid.Kd

    @Kd.setter
    def Kd(self, value):

        try:
            value = float(value)

        except ValueError:
            pass

        else:
            self._settings['pid']['tunings']['Kd'] = value
            self.pid.Kd = value
            self.pid.reset()

    @property
    def pid_sample_time(self) -> float:

        """PID sample time

        :getter: Return the current sample time in seconds
        :setter: Set the new sample time in seconds

        """

        return self.pid.sample_time

    @pid_sample_time.setter
    def pid_sample_time(self, value: float):

        if float(value) <= 0:

            raise ValueError('Sampletime cannot be 0 or less')

        self.pid.sample_time = float(value)
        self._settings['pid']['sample_time'] = self.pid.sample_time

    @property
    def pid_target(self) -> float:

        """Get the current temperature target (PID setpoint).

        :getter: Return the current PID setpoint.
        :setter: Set the PID setpoint after checking boundaries.
        :type: float

        ..note::
            Minimum and maximum values for the setpoint can be set with
            :attr:`Temperatures.target_minimum` or :attr:`Temperatures.target_maximum`.
        """

        return float(self._settings['pid']['setpoint']['current'])

    @pid_target.setter
    def pid_target(self, value: float):

        """Only enforce limits if set.

        """

        try:
            value = float(value)

        except ValueError:
            raise ValueError

        value = max(value, self.pid_target_minimum or value)
        value = min(value, self.pid_target_minimum or value)
        self._settings['pid']['setpoint']['current'] = value
        self.pid.setpoint = self.pid_target
        self.pid.reset()
        self.logger.getChild('PID').info(f'Set target to {value}')

    @property
    def pid_target_minimum(self) -> Union[float, None]:

        """Get the minimum setpoint (PID target) value

        :getter: Return the current minimum setpoint. Default is ``None``.
        :setter: Set a minimum setpoint value.
        :type: float

        .. note::
            :attr:`Temperatures.target_minimum` must be smaller or equal to
            :attr:`Temperatures.target_maximum` (if set).
        """

        return self._settings['pid']['setpoint']['minimum']

    @pid_target_minimum.setter
    def pid_target_minimum(self, value: Union[float, None]):

        """Check that the value is not larger than an existing maximum.
        """

        try:
            value = None if value is None else float(value)

        except ValueError:
            value = None

        if value is not None:
            value = min(value, self.pid_target_maximum or value)

        self.logger.getChild('PID').info(f'Set minimum target to {value}')
        self._settings['pid']['setpoint']['minimum'] = value

    @property
    def pid_target_maximum(self) -> Union[float, None]:

        """Get the maximum setpoint (PID target) value

        :getter: Return the current maximum setpoint. Default is ``None``.
        :setter: set a maximum setpoint value.
        :type: float

        .. note::
            :attr:`Temperatures.target_maximum` must be larger or equal to
            :attr:`Temperatures.target_minimum` (if set).
        """

        return self._settings['pid']['setpoint']['maximum']

    @pid_target_maximum.setter
    def pid_target_maximum(self, value: Union[float, None]):

        try:
            value = None if value is None else float(value)

        except ValueError:
            value = None

        if value is not None:
            value = max(value, self.pid_target_minimum or value)

        self.logger.getChild('PID').debug(f'Set maximum target to {value}')
        self._settings['pid']['setpoint']['maximum'] = value

    @property
    def pid_control(self) -> float:

        """Get the PID control value

        :getter: Calculate the current PID output.
        :setter: Update the current PID value in the settings.
        :type: float
        """

        if self.pid.auto_mode:

            if min((self.current or 1)/(self.pid_target or 1), 1) < 0.75:
                self.__set_slow_mode(True)
            else:
                self.__set_slow_mode(False)

            self.pid_control = self.pid(self.current)

        return self._settings['pid']['output']['current']

    @pid_control.setter
    def pid_control(self, value: float):

        self._settings['pid']['output']['current'] = value

    @property
    def pid_control_min(self) -> Union[float, None]:

        """Get the minimum output limit.

        :getter: Return the minimum output limit.
        :type: float, NoneType
        """

        return self._settings['pid']['output']['minimum']

    @pid_control_min.setter
    def pid_control_min(self, value: Union[float, None]):

        try:
            value = None if value is None else float(value)
        except ValueError:
            value = None

        value = value if value is None else min(value, self.pid_control_max or value)
        self._settings['pid']['output']['minimum'] = value
        self.pid.output_limits = self.pid_control_min, self.pid_control_max
        self.pid.reset()

    @property
    def pid_control_max(self) -> Union[float, None]:

        """Get the maximum output limit.

        :getter: Return the maximum output limit
        :type: float, NoneType
        """

        return self._settings['pid']['output']['maximum']

    @pid_control_max.setter
    def pid_control_max(self, value: Union[float, None]):

        try:
            value = None if value is None else float(value)

        except ValueError:
            value = None

        value = value if value is None else max(value, self.pid_control_min or value)
        self._settings['pid']['output']['maximum'] = value
        self.pid.output_limits = self.pid_control_min, self.pid_control_max
        self.pid.reset()

    def datalogger_collect(self) -> None:

        super().datalogger_collect()

        if 'pid' not in self.datalogger_current:
            self.datalogger_current['pid'] = {}

        self.datalogger_current['pid'].update({
            'control_maximum': self.pid_control_max,
            'control_minimum': self.pid_control_min,
            'control': self.pid_control,
            'target': self.pid_target,
            'target_minimum': self.pid_target_minimum,
            'target_maximum': self.pid_target_maximum,
            'Kp': self.pid.Kp,
            'Ki': self.pid.Ki,
            'Kd': self.pid.Kd,
        })
