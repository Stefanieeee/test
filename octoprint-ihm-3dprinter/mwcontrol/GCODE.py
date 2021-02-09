# coding=utf-8
import numpy as np
import math
from .BaseController import BaseController
from .MCODE import MCODE
import time
import re
import logging


"""GCode的行动命令 初始位置 结束位置 开始时间 feedrate
"""


class GCODEMoveCommand:

    def __init__(self, start_position, start_time, feedrate, end_position, precision=3):
        self.start_position = start_position
        self.end_position = end_position
        self.start_time = start_time
        self.feedrate = feedrate
        self.precision = 3
        self.calc()

    def calc(self):
        xdiff = self.end_position[0]-self.start_position[0]
        ydiff = self.end_position[1]-self.start_position[1]
        zdiff = self.end_position[2]-self.start_position[2]
        self.distance = math.sqrt(math.pow(xdiff, 2) + math.pow(ydiff, 2) + math.pow(zdiff, 2))
        self.end_time = self.start_time + self.travel_duration

    @property
    def feedrate(self):

        return self.__feedrate

    @feedrate.setter
    def feedrate(self, new_feedrate):

        if new_feedrate is not None:
            new_feedrate /= 60

        self.__feedrate = new_feedrate

    @property
    def travel_duration(self):

        if self.feedrate is None:
            return 0

        return self.distance/self.feedrate

    def get_position_at_time(self, timestamp):

        position = [0, 0, 0]

        if timestamp < self.start_time:
            position = self.start_position

        elif timestamp > self.end_time:
            position = self.end_position

        else:
            for n in range(3):
                value = np.interp(timestamp,
                                  [self.start_time, self.end_time],
                                  [self.start_position[n], self.end_position[n]])
                position[n] = round(value, self.precision)

        return position


class PositionBuffer:

    def __init__(self):
        self.__buffer = []
        self.__position_current = [0, 0, 0]
        self.__position_last = [0, 0, 0]

    @property
    def position_last(self):

        if len(self.__buffer):
            self.__position_last = self.__buffer[-1].end_position

        return self.__position_last

    def addCommand(self, position_to, feedrate):
        position_from = self.position_last

        if len(self.__position_buffer):
            time_start = self.__buffer[-1].end_time
        else:
            time_start = time.time()

        element = GCODEMoveCommand(position_from, time_start, feedrate, position_to)
        self.__buffer.append(element)

    @property
    def position_estimated(self):

        position = self.position_last
        feedrate = self.__gcode_feedrate_last

        while len(self.__position_buffer):
            command = self.__position_buffer[0]
            now = time.time()

            if now < command.end_time:
                position, feedrate = command.get_position_at_time(now), command.feedrate
                break

            # elif now > command.end_time:
            self.__position_buffer.pop(0)

            if not len(self.__position_buffer):
                self.__gcode_position_last = command.end_position
                self.__gcode_feedrate_last = 0

        return {'x': position[0], 'y': position[1], 'z': position[2], 'feedrate': feedrate}



class DIN_GCODE(BaseController):

    """Parse GCODE commands.

    **Supported commands**

    +---------+----------------------------------------------------------------------------------+
    | Command | Description                                                                      |
    +=========+==================================================================================+
    | G0, G1  | Lineare move commands                                                            |
    +---------+----------------------------------------------------------------------------------+
    | G2, G3  | Arc move commands                                                                |
    +---------+----------------------------------------------------------------------------------+
    | G5      |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G20     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G21     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G29     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G90     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G91     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+
    | G92     |                                                                                  |
    +---------+----------------------------------------------------------------------------------+

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__feedrate = 0   # Feedrate
        self.gcode_absolute_positions = True
        self.gcode_travel_distance = 0.0   # Travel distance
        self.gcode_extrusion_distance = 0.0
        self.gcode_extrusion_position = 0.0
        self.__gcode_position_last = [0, 0, 0]
        self.__gcode_feedrate_last = 0
        self.__logger = logging.getLogger('MCS.GCODE')
        self.__pass_callbacks = {
            'G0': self.__G1,       # Linear move
            'G1': self.__G1,       # Linear move
            'G28': self.__G28,
            'G90': self.__G90,     # Absolute position
            'G91': self.__G91,     # Relative position
            'G92': self.__G92,
        }
        self.__absorb_callbacks = {}
        self.__position_buffer = []

    def __position_buffer_add(self, end_position, feedrate):

        start_position = self.gcode_position_last.copy()

        if len(self.__position_buffer):
            start_time = self.__position_buffer[-1].end_time
        else:
            start_time = time.time()

        element = GCODEMoveCommand(start_position, start_time, feedrate, end_position)
        self.__position_buffer.append(element)

    @property
    def gcode_position_estimated(self):

        position = self.gcode_position_last.copy()
        feedrate = self.__gcode_feedrate_last

        while len(self.__position_buffer):
            command = self.__position_buffer[0]
            now = time.time()

            if now < command.end_time:
                position, feedrate = command.get_position_at_time(now), command.feedrate
                break

            # elif now > command.end_time:
            self.__position_buffer.pop(0)

            if not len(self.__position_buffer):
                self.__gcode_position_last = command.end_position
                self.__gcode_feedrate_last = 0

        return {'x': position[0], 'y': position[1], 'z': position[2], 'feedrate': feedrate}

    @property
    def gcode_position_last(self):

        if len(self.__position_buffer):
            self.__gcode_position_last = self.__position_buffer[-1].end_position

        return self.__gcode_position_last

    @property
    def gcode_feedrate_last(self):

        return self.__gcode_feedrate_last

    @gcode_feedrate_last.setter
    def gcode_feedrate_last(self, value):

        self.__gcode_feedrate_last = value

    def parseFeedrateFromGCODE(self, message: str):
        feedrate_regex = r'[fF][\d.]+'

        try:
            feedrate = re.findall(feedrate_regex, message)[0][1:]
        except IndexError:
            # Nothing found
            return None

        try:
            feedrate = float(feedrate)
        except ValueError:
            self.__logger.error(f'Could not parse feedrate from {message}')
            return None

        return feedrate

    def parseGCODE(self, message: str):
        # valid_gcode_regex = r'[a-zA-Z][\d.]+'
        # message_exploded = re.findall(valid_gcode_regex, message.split(';')[0])
        # command = message_exploded[0]
        # parameters = message_exploded[1:] if len(message_exploded) > 1 else []
        # OLD

        message = message.replace('\t', ' ').rstrip().split(';')[0].rstrip()

        if len(message) == 0 or message[0] not in ['M', 'G']:   # Ignore if there is no command
            return False

        message = message.split(' ')  # Split the command and arguments
        parameters = message[1:] if len(message) > 1 else []
        command = message[0]
        # OLD
        msg = ' '.join(message)
        self.__logger.debug(f'Receive message "{msg}"')
        return command, parameters

    @property
    def __callbacks(self):

        return {**self.__pass_callbacks, **self.__absorb_callbacks}

    @property
    def gcodes_supported(self):

        return self.gcodes_pass + self.gcodes_absorb

    @property
    def gcodes_absorb(self):

        return [code for code, _ in self.__absorb_callbacks.items()] + self.mcodes_absorb

    @property
    def gcodes_pass(self):

        return [code for code, _ in self.__pass_callbacks.items()] + self.mcodes_pass

    def collect_data(self):

        super().collect_data()

    def onGCODE(self, message=None, command=None, parameters=None):

        """Process the GCODE command and call the right callback

        :param message: GCODE message
        :type message: str
        :return: True if command parsed successfully, False otherwise
        :rytpe: boolean
        """
        # Replace tabs, remove whitespaces, ignore ; comments
        # Dismantle the command, valid vor all GCODE commands

        if message is not None:
            command, parameters = self.parseGCODE(message)
        elif (command is None) and (parameters is None):
            raise Exception

        if command not in self.gcodes_supported:
            raise UnsupportedGCODEException(command)

        if command[0] == 'M':
            self.onMCODE(command=command, parameters=parameters)
            return

        try:
            self.__callbacks[command](parameters)
        except GCODEParameterError:
            return False

        return True

    @property
    def gcode_feedrate(self):

        return self.__feedrate

    @gcode_feedrate.setter
    def gcode_feedrate(self, value):

        try:
            value = float(value)
        except ValueError:
            self.__logger.error(f'Could not read feedrate {value}')
            return # Do nothing

        if value != self.__feedrate:
            self.__logger.info(f'Set feedrate to {value}')
            self.__feedrate = value

    def __G1(self, args):
        """Get the new position

        :param args: Variable list of arguments for G1, e.g. ``['X0', 'Y10.2', 'Z0.2']``
        :type args: list
        :return: True if all parameters are correct
        :rtype: boolean
        :raises: GCODEUnsupportedParameterError, GCODEParameterError, GCODEFloatValueError,
            GCODEmptyParameterError

        .. note::
            This command can be used for G0 as well without modification

        *GCODE syntax*
        ``G1 [X<float, position>] [Y<float, position>] [Z<float, position>] [F<float, feedrate>]
            [E<float, extrusion>]``

        *GCODE example*
        - ``G1 X0 F1000 E100 ; ``

        """
        # https://reprap.org/wiki/G-code#G0_.26_G1:_Move
        position = self.gcode_position_last.copy()

        if not (0 < len(args) <= 5):  # Do nothing if no arguments are supplied.
            return False

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            # Check if all supplied arguments are allowed
            if parameter not in ['X', 'Y', 'Z', 'E', 'F']:
                raise GCODEUnsupportedParameterError

            if len(value) == 0:
                return False

            try:  # Check if the set value is a float.
                value = float(value)

            except ValueError:
                raise GCODEFloatParameterError(f'Value {value} is not float', logger=self.__logger)

            except Exception:  # Raise meta exception if something goes wrong here
                raise GCODEParameterError(logger=self.__logger)

            if parameter == 'X':
                position[0] = value

            elif parameter == 'Y':
                position[1] = value

            elif parameter == 'Z':
                position[2] = value

            # elif parameter == 'F':
            #     self.gcode_feedrate = value

            elif parameter == 'E':
                self.gcode_extrusion_position = value

        # command_travel_distance = np.linalg.norm(position-self.gcode_position_last)
        # self.gcode_travel_distance += command_travel_distance
        # self.__position_buffer_add(position, self.gcode_feedrate)

        # if getattr(self, 'filament_sensor_virtual', False):
            # if self.gcode_feedrate is not None:
            #     if command_travel_distance > 0:
            #         self.filament_sensor_virtual.calc_speed(command_travel_distance, self.gcode_feedrate)

        return True

    def __G28(self, args):

        position = self.gcode_position_last.copy()

        if not len(args):
            args = ['X', 'Y', 'Z']

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            if parameter not in ['X', 'Y', 'Z']:
                raise GCODEUnsupportedParameterError

            if parameter == 'X':
                position[0] = 0.0

            if parameter == 'Y':
                position[1] = 0.0

            if parameter == 'Z':
                position[2] = 0.0

        self.__position_buffer_add(position, None)

    def __G90(self, args):

        self.gcode_absolute_positions = True

    def __G91(self, args):

        self.gcode_absolute_positions = False

    def __G92(self, args):

        """Set the absolute position

        :param args: Variable list of arguments for G92, e.g. ``['X0', 'Y0', 'Z0']``
        :type args: list
        :return: True if all parameters are correct
        :rtype: boolean
        :raises: GCODEUnsupportedParameterError, GCODEParameterError, GCODEFloatParameterError,
            GCODEmptyParameterError

        *GCODE syntax*
        ``G92 [X<float, position>] [Y<float, position>] [Z<float, position>]
            [E<float, extrusion>]``

        .. note::
            This command can be used without any additional parameters. Calling ``G92`` is mapped
            to ``G92 X0 Y0 Z0 E0``

        *GCODE example*
        - ``G92 X0 Y0 Y0 ; Set current position as origin (0, 0, 0)`

        """
        # https://reprap.org/wiki/G-code#G92:_Set_Position

        if len(args) == 0:
            args = ['X0', 'Y0', 'Z0', 'E0']

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            # Check if all supplied arguments are allowed
            if parameter not in ['X', 'Y', 'Z', 'E']:
                raise GCODEUnsupportedParameterError

            try:  # Check if the set value is a float.
                float(value)

            except ValueError:
                if not len(value):  # silently ignore paramwordeters without value
                    raise GCODEmptyParameterError
                raise GCODEFloatParameterError

            except Exception:  # Raise meta exception if something goes wrong here

                raise GCODEParameterError(logger=self.__logger)

            # if parameter == 'X':
            #     self.gcode_travel_position[0] = value
            #
            # elif parameter == 'Y':
            #     self.gcode_travel_position[1] = value
            #
            # elif parameter == 'Z':
            #     self.gcode_travel_position[2] = value

            if parameter == 'E':
                self.gcode_extrusion_position = value

        return True


class GCODE(DIN_GCODE, MCODE):

    pass


class GCODEException(Exception):
    """Base class for GCODE exceptions"""

    def __init__(self, *args, **kwargs):

        self.message = args[0] if args else 'No message available'
        self.logger = kwargs.get('logger', False)

        if self.logger and self.message:
            self.logger.warning(self.message)


class UnsupportedGCODEException(GCODEException):
    """Base class for unsupported GCODE commands"""

    def __str__(self):

        return f'Unsupported GCODE: {self.message}'


class GCODEParameterError(GCODEException):
    """Base class froo GCODE parameter errors"""

    def __str__(self):

        return f'GCODE parameter error: {self.message}'


class GCODEUnsupportedParameterError(GCODEParameterError):
    """Raised if there is a GCODE parameter supplied that is not availavle with this GCODE"""

    pass


class GCODEFloatParameterError(GCODEParameterError):

    pass


class GCODEmptyParameterError(GCODEParameterError):

    pass
