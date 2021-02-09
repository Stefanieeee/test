# coding=utf-8
import logging
from .BaseController import BaseController
from .PIDMixin import PIDMixin


"""Octoprint中的喷嘴温度
"""

class Temperature(BaseController):

    """Base class for temperature handling.

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._settings['current'] = 0.0

    @property
    def current(self):

        """Get the current tenperature.

        :getter: Return the current temperature in *Degree Celcius [°C]*.
        :setter: Set a new temperature in *Degree Celcius [°C]*.
        :type: float
        """

        return self._settings['current']

    @current.setter
    def current(self, value):

        try:
            value = float(value)

        except ValueError:
            value = None

        self._settings['current'] = value

    def datalogger_collect(self):

        """Add data to the datalogger collection.

        """

        super().datalogger_collect()
        self.datalogger_current.update({
            'current': self.current or 0.0,
            'target': self.pid_target or 0.0
        })

class NozzleTemperature(PIDMixin, Temperature):

    """Extend :class:`Temperatures` for usage within an OctoPrint plugin as virtual nozzle

    :param settings: Overwrite default settings with settings in this dictionary. Default is ``{}``.
    :type settings: dict, optional
    """

    pass
