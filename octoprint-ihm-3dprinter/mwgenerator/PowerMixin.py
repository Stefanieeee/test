import math

"""功率
"""

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
