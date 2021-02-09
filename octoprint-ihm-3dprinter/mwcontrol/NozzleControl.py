# coding=utf-8

import logging
import mwgenerator
from .BaseController import BaseController
from .GCODE import GCODE
from .Temperature import NozzleTemperature
from .RemoteSensor import TemperatureSensor
from .RemoteSensor import FilamentSensor
from .RemoteSensor import PyrometerTemperatureSensor
from .RemoteSensor import VirtualFilamentSensor
from .RemoteSensor import MicrowavePowerSensor
from typing import Union

from .ModelControlModeMixin import ModelControlModeMixin
from .PIDControlModeMixin import PIDControlModeMixin

"""微波打印头设置
"""


class NozzleControl(PIDControlModeMixin, ModelControlModeMixin, GCODE, BaseController):

    """Main class for controlling the microwave nozzle

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__logger = self.logger.getChild('MCS')
        self.__state = None

        # Heating system
        self.heater = mwgenerator.ExtendedClient()
        self.heater.logger.setLevel(getattr(logging, 'INFO'))

        # Temperature controller
        self.temperature = NozzleTemperature()

        # Thermal image sensor
        self.sensor = TemperatureSensor()
        self.sensor.bind()

        # Filament speed sensor
        self.filament_sensor = FilamentSensor()
        self.filament_sensor.connection_port = 2343
        self.filament_sensor.bind()

        # Pyrometer sensor
        self.pyrometer_sensor = PyrometerTemperatureSensor()
        self.pyrometer_sensor.connection_port = 2344
        self.pyrometer_sensor.bind()

        self.microwave_sensor = MicrowavePowerSensor()
        self.microwave_sensor.connection_port = 2345
        self.microwave_sensor.bind()

        # Virtual filament sensor
        self.filament_sensor_virtual = VirtualFilamentSensor()

    @classmethod
    def get_defaults(self) -> dict:

        """Return the default values for this class

        """

        defaults = {
            'active': False,
            'mode': None,  # None,
            'model': {
                'offset': None,
                'coefficient': None,
                'sensor': 'GCODE'
            },
        }

        return defaults

    def stop(self) -> None:

        """Stop a running pring process

        """

        self.heater.active = 0
        self.heater.power = self.heater.power_step
        self.heater.ontime = self.heater.ontime_min
        self.temperature.pid_target = 0
        self.control_mode = None
        self.__logger.info('Printer is stopped, disable Microwave Control System')

    def pause(self) -> None:

        """Pause a running print process

        """

        self.__previous_status = {
            'heater_active': self.heater.active,
            'mode': self.control_mode
        }
        self.heater.active = 0
        self.__logger.info('Printer is paused, disable Microwave Control System')

    def resume(self) -> None:

        """Resume a paused printing process

        """

        self.heater.active = self.__previous_status['heater_active']
        self.control_mode = self.__previous_status['mode']
        self.__logger.info('Printer is resuming, set Microwave Control System to previous state')

    def update_settings(self, settings: dict = {}, *args, **kwargs):

        """Update the settings

        """

        super().update_settings(settings=settings, *args, **kwargs)

        if 'nozzlecontrol' not in self._settings:
            self._settings['nozzlecontrol'] = NozzleControl.get_defaults()

    @property
    def control_mode(self) -> Union[str, None]:

        """The control mode currently active

        :getter: Return the current control mode
        :setter: Set a new control mode
        """

        return self._settings['nozzlecontrol']['mode']

    @control_mode.setter
    def control_mode(self, mode: Union['str, None']):

        if mode is None:
            self._settings['nozzlecontrol']['mode'] = None

        elif mode in ['MANUAL', 'PRESET', 'MODEL', 'PID']:
            self._settings['nozzlecontrol']['mode'] = mode

        else:
            self.__logger.warning(f'Unsupported mode {mode}')

        if mode != 'PID':
            self.temperature.pid.set_auto_mode(False)

    @property
    def active(self):

        return self._settings['nozzlecontrol']['active']

    @active.setter
    def active(self, value):

        self._settings['nozzlecontrol']['active'] = bool(value)

    def datalogger_collect(self):

        """Collect and process all datalogger values
        """

        super().datalogger_collect()

        self.datalogger_current['control'] = {
            'mode': self.control_mode,
            'model': {
                'offset': self.model_offset,
                'coefficient': self.model_scalar,
                'sensor': self.model_sensor
            }
        }
        # All the components to collect data from
        components = [
            'heater',
            'temperature',
            'sensor',
            'filament_sensor',
            'pyrometer_sensor',
            'filament_sensor_virtual',
            'microwave_sensor'
        ]

        self.filament_sensor_virtual.speed = self.gcode_position_estimated['feedrate']

        for target_name in components:
            target = getattr(self, target_name)
            target.datalogger_collect()
            self.datalogger_current[target_name] = target.datalogger_current.copy()

        self.datalogger_run()

    def control_manual(self):

        """Control loop for manual control

        """

        self.heater.rf = self.heater.active

    def control_preset(self):

        pass

    def control(self):

        """Main control method

        """

        if not self.heater.available:
            self.heater.active = 0

        if self.sensor.out_of_range and self.heater.active:
            self.__logger.error('Temperature sensor is out of range!')
            self.stop()

        if self.pyrometer_sensor.out_of_range and self.heater.active:
            self.__logger.error('Pyrometer sensor is out of range!')
            self.stop()

        if self.control_mode == 'PID':
            self.control_pid()

        elif self.control_mode == 'MANUAL':
            self.control_manual()

        elif self.control_mode == 'MODEL':
            self.control_model()

        elif self.control_mode == 'PRESET':
            pass
