import logging

"""PID控制
"""


class PIDControlModeMixin:

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__logger = logging.getLogger('MCS.Control.PID')

    def control_pid(self):

        """Control loop for the PID control mode

        """

        # Do nothing is heating system is not active
        if not self.sensor.available:
            self.__logger.error('Filament temperature sensor not available')
            self.stop()

        if not self.heater.active:
            self.temperature.pid.set_auto_mode(False)
            self.temperature.pid_control = 0
            return

        elif not self.temperature.pid.auto_mode:
            self.temperature.pid.set_auto_mode(True, 0)

        # Write the current measured temperature to the PID control
        self.temperature.current = self.sensor.value

        # Make sure heating system is enabled
        self.heater.rf = 1
        self.heater.pwm = self.temperature.pid_control/100
