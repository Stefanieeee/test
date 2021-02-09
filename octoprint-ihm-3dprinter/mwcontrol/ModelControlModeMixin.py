
import logging

"""模型控制设置
"""

class ModelControlModeMixin:

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__logger = logging.getLogger('MCS.Control.Model')

    def model_calc_power(self, speed, offset=None, coefficient=None):

        offset = offset or self.model_offset
        coefficient = coefficient or self.model_scalar

        return offset + speed * coefficient

    @property
    def model_offset(self):

        return self._settings['nozzlecontrol']['model']['offset']

    @model_offset.setter
    def model_offset(self, value):

        self._settings['nozzlecontrol']['model']['offset'] = float(value)

    @property
    def model_scalar(self):

        return self._settings['nozzlecontrol']['model']['coefficient']

    @model_scalar.setter
    def model_scalar(self, value):

        self._settings['nozzlecontrol']['model']['coefficient'] = float(value)

    @property
    def model_sensor(self):

        return self._settings['nozzlecontrol']['model']['sensor']

    @model_sensor.setter
    def model_sensor(self, value):

        if value in ['GCODE', 'EXTERNAL1']:
            self._settings['nozzlecontrol']['model']['sensor'] = value
            self.__logger.info(f'Set speed sensor to {self.model_sensor}')

    def control_model(self, speed=None):

        """Control loop for the model based control mode

        """

        if any([not self.heater.active, self.control_mode != 'MODEL']):
            return  # Nothing to do if heating system is not active

        for attr in ['model_offset', 'model_scalar']:
            if getattr(self, attr, None) is None:
                # Nothing to do if model does not have all requires values set
                return

        if self.model_sensor == 'EXTERNAL1':

            """Real filament speed sensor
            """

            if (self.filament_sensor.available) and (self.filament_sensor.speed is not None):
                # Only run if the sensors are available and returning valid data
                self.heater.rf = 1
                self.heater.pwm_power = self.model_calc_power(speed=self.filament_sensor.speed)
            else:
                # Sensore are not available or returning unusable data, disable the heating.
                self.stop()

        elif self.model_sensor == 'GCODE':

            self.heater.rf = 1
            self.heater.pwm_power = self.model_calc_power(speed=self.gcode_feedrate/60)

        else:

            self.__logger.warning(f'Unkown sensor {self.model_sensor}')
            self.stop()
