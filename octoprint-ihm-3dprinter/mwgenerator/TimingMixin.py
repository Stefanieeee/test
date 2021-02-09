class TimingMixin:


"""PWM导通时间 Maximum and Minimum
"""



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
            value = max(value, self.offtime_minimum)
            value = min(value, self.offtime_maximum)
            self.logger.debug(f'Set offtime to {value}ns')
            super(ExtendedClient, self.__class__).offtime.fset(self, value)

    @property
    def offtime_maximum(self):

        return self._settings['offtime']['maximum']

    @offtime_maximum.setter
    def offtime_maximum(self, value):

        try:
            value = float(value)
        except ValueError:
            self.logger.warning('Could not parse offtime_maximum as float')
        else:
            value = max(value, ExtendedClient.get_defaults['offtime']['maximum'])
            self.logger.debug(f'Set offtime_maximum to {value}')
            self._settings['offtime']['maximum'] = value

    @property
    def offtime_minimum(self):

        return self._settings['ontime']['minimum']

    @offtime_minimum.setter
    def offtime_minimum(self, value):

        try:
            value = float(value)
        except ValueError:
            self.logger.warning('Could not parse offtime_minimum as float')
        else:
            value = max(value, ExtendedClient.get_defaults['offtime']['minimum'])
            self.logger.debug(f'Set offtime_minimum to {value}ns')
            self._settings['offtime']['minimum'] = value
