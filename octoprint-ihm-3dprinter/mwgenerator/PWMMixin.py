class PWMMixin:

"""PWM脉宽调制
"""


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

        if value is None:
            value = ExtendedClient.get_defaults()['pwm_period']['minimum']

        try:
            value = float(value)
        except ValueError:
            self.logger.warning('Could not parse pwm_period_minimum as float')

        value = max(value, self.pwm_period_minimum)
        value = min(value, ExtendedClient.get_defaults()['pwm_period']['maximum'])
        self.logger.debug(f'Set minimum PWM period to {value}')
        self._settings['pwm_period']['minimum'] = value

    @property
    def pwm_period_maximum(self):

        return self.ontime_max + self.offtime_maximum

    @pwm_period_maximum.setter
    def pwm_period_maximum(self, value):

        if value is None:
            value = ExtendedClient.get_defaults()['pwm_period']['maximum']

        try:
            value = float(value)
        except ValueError:
            self.logger.warning('Could not parse pwm_power_max as float')

        value = min(value, self.pwm_period_maximum)
        value = max(value, ExtendedClient.get_defaults()['frequency']['minimum'])
        self.logger.debug(f'Set maximum PWM period to {value}')
        self._settings['pwm_power_max']['maximum'] = value

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
