# coding=utf-8
from typing import Union, List
from .BaseController import BaseController
import logging

"""MCode指令
"""


class MCODE(BaseController):

    """Parse and special MCODE commands to configure the system.

    +---------+------------+-----------------------------------------------------------------------+
    | Command | Options    | Description                                                           |
    +=========+============+=======================================================================+
    | M1003   | RF         | Enable/Disable the RF output                                          |
    +---------+------------+-----------------------------------------------------------------------+
    | M400    | ACTIVE     | Enable/Disable the active mode                                        |
    +---------+------------+-----------------------------------------------------------------------+
    | M401    | MIN MAX    | Set minimum and maximum ontime                                        |
    +---------+------------+-----------------------------------------------------------------------+
    | M402    | OFFT       | Set offtime                                                           |
    +---------+------------+-----------------------------------------------------------------------+
    | M403    | MIN MAX    | Set minimum and maximum power                                         |
    +---------+------------+-----------------------------------------------------------------------+
    | M404    | STEP       | Set the power step                                                    |
    +---------+------------+-----------------------------------------------------------------------+
    | M405    | FREQ       | Set the frequency                                                     |
    +---------+------------+-----------------------------------------------------------------------+
    | M406    | MODE       | Set the operation mode                                                |
    +---------+------------+-----------------------------------------------------------------------+
    | M407    | LOCK       | Lock the options                                                      |
    +---------+------------+-----------------------------------------------------------------------+
    | M408    | IP PORT    | Address of the microwave system                                       |
    +---------+------------+-----------------------------------------------------------------------+
    | M409    | MAX        | Amplifier temperature limit                                           |
    +---------+------------+-----------------------------------------------------------------------+

    **Title**

    +---------+------------+-----------------------------------------------------------------------+
    | Command | Options    | Description                                                           |
    +=========+============+=======================================================================+
    | M104    | MIN MAX    | Set temperature                                                       |
    +---------+------------+-----------------------------------------------------------------------+
    | M149    | K F C      | Set temperature unit                                                  |
    +---------+------------+-----------------------------------------------------------------------+
    | M410    | MIN MAX    | Set minimum and maximum temperature                                   |
    +---------+------------+-----------------------------------------------------------------------+
    | M411    | P I D      | Set PID values                                                        |
    +---------+------------+-----------------------------------------------------------------------+
    | M412    | MAX MIN    | Set minimum and maximum control output                                |
    +---------+------------+-----------------------------------------------------------------------+
    | M413    | SAMPLE     | Set PID sample time                                                   |
    +---------+------------+-----------------------------------------------------------------------+
    | M414    | RUN        | Start or stop the control loop                                        |
    +---------+------------+-----------------------------------------------------------------------+

    +---------+------------+-----------------------------------------------------------------------+
    | Command | Options    | Description                                                           |
    +=========+============+=======================================================================+
    | M415    | RUN        | Start or stop the main loop                                           |
    +---------+------------+-----------------------------------------------------------------------+

    +---------+------------+-----------------------------------------------------------------------+
    | Command | Options    | Description                                                           |
    +=========+============+=======================================================================+
    | M1000   |            | Select the control mode                                               |
    +---------+------------+-----------------------------------------------------------------------+
    | M1001   |            | Set the value for the model offset                                    |
    +---------+------------+-----------------------------------------------------------------------+
    | M1002   |            | Set the value for the model coefficient                               |
    +---------+------------+-----------------------------------------------------------------------+
    | M1003   |            | Set the HF RF                                                         |
    +---------+------------+-----------------------------------------------------------------------+
    | M1004   |            | Set the value for the model source                                    |
    +---------+------------+-----------------------------------------------------------------------+
    | M1010   |            | Start the datalogger                                                  |
    +---------+------------+-----------------------------------------------------------------------+
    | M1011   |            | Stop the datalogger                                                   |
    +---------+------------+-----------------------------------------------------------------------+
    | M1012   |            | Write datalogger to file                                              |
    +---------+------------+-----------------------------------------------------------------------+


    *Sensor commands*

    +---------+-----------------+------------------------------------------------------------------+
    | Command | Options         | Description                                                      |
    +=========+=================+==================================================================+
    | M1020   | P<id> S<min>    | Set the minimum sensor value                                     |
    +---------+-----------------+------------------------------------------------------------------+
    | M1021   | P<id> S<max>    | Set the maximum sensor value                                     |
    +---------+-----------------+------------------------------------------------------------------+
    | M1022   | P<id> S<offset> | Set the value for the sensor offset                              |
    +---------+-----------------+------------------------------------------------------------------+
    | M1023   | P<id> S<coeff>  | Set the value for the sensor coefficient                         |
    +---------+-----------------+------------------------------------------------------------------+
    | M1024   | P<id> S<val>    | Set the fallback value                                           |
    +---------+-----------------+------------------------------------------------------------------+

    *Micorwave commands*
    +---------+-----------------+------------------------------------------------------------------+
    | Command | Options         | Description                                                      |
    +=========+=================+==================================================================+
    | M1030   | P<state>        | Enable (1) or disable (0) the RF output                          |
    +---------+-----------------+------------------------------------------------------------------+
    | M1031   | P<mode_id>      | Change the operation mode (0: PWM, 1: CW)                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1032   | P<pwm_power>    | Set a target PWM power                                           |
    +---------+-----------------+------------------------------------------------------------------+
    | M1033   | [P<id>] S<value>| PWM pulse duration: set the value (id: 0), minimum (id: 1) and   |
    |         |                 | maximum (id: 2). Default id is 0.                                |
    +---------+-----------------+------------------------------------------------------------------+
    | M1034   | [P<id>] S<value>| PWM on-time: Set the value (id: 0), minimum (id: 1) and maximum  |
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1034   | [P<id>] S<value>| PWM off-time: set the value (id: 0), minimum (id: 1) and maximum |
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1035   | [P<id>] S<value>| Frequency: set the value (id: 0), minimum (id: 1) and maximum    |
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1036   | [P<id>] S<value>| Power: set the value (id: 0), minimum (id: 1), maximum (id: 2)   |
    |         |                 | and step (id: 3). Default id is 0.                               |
    +---------+-----------------+------------------------------------------------------------------+
    | M1037   | [P<id>] S<value>| Temperature: set the value (id: 0), minimum (id: 1) and maximum  |
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1038   | [P<id>] S<value>| Forward power: set the value (id: 0), minimum (id: 1) and maximum|
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+
    | M1039   | [P<id>] S<value>| Reverse power: set the value (id: 0), minimum (id: 1) and maximum|
    |         |                 | (id: 2). Default id is 0.                                        |
    +---------+-----------------+------------------------------------------------------------------+

    .. note::
        This will overwrite settings you might have done before.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__bed_temperature = 0
        self.__logger = logging.getLogger('MCS.MCODE')
        # self._MCODEcallbacks = {}
        self.__sensor_map = ['sensor', 'filament_sensor', 'pyrometer_sensor']

        self.__passthrough_callbacks = {
            'M0': self.__M0,
            'M1': self.__M0,
            'M112': self.__M112,
            'M149': self.__set_temperature_unit,  # Temperature units
        }

        self.__absorb_callbacks = {
            'M104': self.__set_temperature,         # Set the temperature
            'M1040': self.__set_hf_active,
            'M401': self.__set_hf_ontime_limits,    # Ontime MIN MAX
            'M402': self.__set_hf_offtime,          # Offtime OFFT
            'M403': self.__set_hf_power_limits,     # Power MIN MAX
            'M404': self.__set_hf_power_step,       # Step STEP
            'M405': self.__set_hf_frequency,        # Frequency FREQ
            'M406': self.__set_hf_mode,             # Mode MODE
            'M407': self.__set_hf_lock,             # Mode MODE
            'M408': self.__set_hf_connection,
            'M409': self.__set_hf_temperature_limits,
            # 'M_': lambda args: self.__preset(args),
            # 'M__': lambda args: self.__link_preset_to_feedrate(args),
            'M410': self.__set_temperature_limits,  # Temperature MIN MAX
            'M411': self.__set_pid_terms,           # PID values P I D
            'M412': self.__set_pid_limits,          # PID output MIN MAX
            'M413': self.__set_pid_sample_time,     # Sampletime SAMPLE
            # Commands for the microwave control system
            'M1000': self.__M1000,
            'M1001': self.__M1001,
            'M1002': self.__M1002,
            'M1003': self.__set_hf_rf,
            'M1004': self.__M1004,
            'M1010': self.__M1010,
            'M1011': self.__M1011,
            'M1012': self.__M1012,
            # MCODE for sensors
            'M1020': self.__M1020,
            'M1021': self.__M1021,
            'M1022': self.__M1022,
            'M1023': self.__M1023,
            'M1024': self.__M1024,
            # Micorwave generator new commands
            'M1030': self.__M1030,
            'M1031': self.__M1031,
            'M1032': self.__M1032,

        }

    @property
    def mcodes_supported(self) -> List[str]:

        """All supported MCODE commands

        :getter: Returns a list of all suported commands

        .. note::
            The returned list is a union of mcodes_absorb and mcodes_pass

        """

        return self.mcodes_pass + self.mcodes_absorb

    @property
    def mcodes_absorb(self) -> List[str]:

        """All MCODES to be absorbed by the MCS

        :getter: Returns a list of all commands to be absorbed

        """

        return [code for code, _ in self.__absorb_callbacks.items()]

    @property
    def mcodes_pass(self):

        """All MCODES to be passed through by the MCS

        :getter: Returns a list of all commands to be passed through

        """

        return [code for code, _ in self.__passthrough_callbacks.items()]

    @property
    def __callbacks(self):

        """All MCODES with respective callbacks

        """

        return {**self.__absorb_callbacks, **self.__passthrough_callbacks}

    def collect_data(self):

        super().collect_data()

    def onMCODE(self, message=None, command=None, parameters=None) -> bool:

        """Analyse the provided MCODE message and call the corresponding callback.

        :param message: The command message, e.g.: ``M400 ...``
        :type message: str
        :return: ``True`` is MCODE parsed successfull, ``False`` otherwise
        :rtype: bool
        :raises: UnsupportedMCODEException
        """

        # Dismantle the command, valid vor all GCODE commands
        if message is not None:
            command, parameters = self.parseGCODE(message)
        elif (command is None) and (parameters is None):
            raise Exception

        if command[0] != 'M':
            return False  # Ignore if it is not an M-command

        if command not in self.mcodes_supported:
            raise UnsupportedGCODEException(command)

        try:
            self.__callbacks[command](parameters)
        except MCODEParameterError:
            return False

        return True

    def __M0(self, args: list) -> bool:

        """M0, M1 - Unconditional stop

        The M0 and M1 commands pause after the last movement and wait for the user to continue.
        M1 is a deprecated alias for M0.

        .. code-block:: none
            :linenos:
            M0 ; Stop and wait
        """

        self.stop()

        return True

    def __M112(self, args: list) -> bool:

        """M112 - Emergency Stop

        Used for emergency stopping, M112 shuts down the machine, turns off all the steppers and
        heaters, and if possible, turns off the power supply. A reset is required to return to
        operational mode.

        .. note::
            M112 is the fastest way to shut down the machine using a host, but it may need to wait
            for a space to open up in the command queue.

        .. code-block:: none
            :linenos:
            M112 ; Emergency stop
        """

        self.stop()

        return True


    def __datalogger_record_limit_count(self, args: list) -> bool:

        """Set the number of values the datalogger should record before stopping.
        """

        if len(args) != 1:
            return False

        if args[0][0] != 'P':
            return False

        try:
            count = int(args[1:])
        except ValueError:
            raise MCODEParameterError

        else:
            _ = count

    def __datalogger_record_limit_time(self, args: list) -> bool:

        """Set the time (in ms) the datalogger should record before stopping.
        """

        pass

    def __M1000(self, args: list) -> bool:

        """
        *MCODE syntax*
        ``Mxxx MANUAL | PRESET | PID | MODEL``
        """

        if len(args) != 1:
            return False

        mode = args[0]

        if mode in ['MANUAL', 'PRESET', 'PID', 'MODEL']:
            self.control_mode = mode
            return True

        return False

    def __M1001(self, args: list) -> bool:

        """
        *MCODE syntax*
        ``Mxxx P<float>``
        """

        if len(args) != 1 or args[0][0] != 'P':
            return False

        value = args[0][1:]
        self.model_offset = value

    def __M1002(self, args: list) -> bool:
        """
        *MCODE syntax*
        ``Mxxx P<float>``
        """

        if len(args) != 1 or args[0][0] != 'P':
            return False

        value = args[0][1:]
        self.model_scalar = value

    def __M1004(self, args: list) -> bool:
        """
        *MCODE syntax*
        ``M1004 P<int>``
        """

        if len(args) != 1 or args[0][0] != 'P':
            return False

        value = args[0][1:]
        sensor_names = ['GCODE', 'EXTERNAL1']
        try:
            sensor = sensor_names[int(value)]
        except IndexError:
            self.__logger.error(f'Unknown sensor ID {value}')
        else:
            self.model_sensor = sensor

    def __M1010(self, args: list) -> bool:

        """M1010 - Start the datalogger

        .. code-block:: none
            :linenos:
            M1010 ; Start the datalogger
        """

        self.datalogger_start()

        return True

    def __M1011(self, args: list) -> bool:

        """M1011 - Stop datalogger

        .. note::
            This will automatically write the remaining content to a file.

        .. code-block:: none
            :linenos:
            M1011 ; Stop datalogger
        """

        self.datalogger_stop()

        return True

    def __M1012(self, args: list) -> bool:

        """M1012 - Write datalogger to file

        .. code-block:: none
            :linenos:
            M1012 ; Write datalogger to file
        """

        self.datalogger_dump()

        return True

    def __M1020(self, args: list) -> bool:

        """M1020 - Set sensor minimum

        *Command syntax*

        ``M1020 P<sensor id> [S[minimum]]``

        .. code-block:: none
            :linenos:
            M1020 P1 S50    ; Set minimum for sensor 1 to 50
            M1020 P1 S      ; Disable minimum for sensor 1
            M1020 P1        ; Disable minimum for sensor 1
        """

        if len(args) > 2:
            return False

        new_minimum = None
        sensor_id = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['P', 'S']:
                continue

            if parameter == 'P' and len(value):
                sensor_id = int(value)
            elif parameter == 'S' and len(value):
                new_minimum = value

        if sensor_id is None:
            return False

        sensor = getattr(self, self.__sensor_map[sensor_id], False)
        sensor.minimum = new_minimum

        return True

    def __M1021(self, args: list) -> bool:

        """M1021 - Set sensor maximum

        *Command syntax*

        ``M1021 P<sensor id> [S[maximum]]``

        .. code-block:: none
            :linenos:
            M1021 P1 S50    ; Set maximum for sensor 1 to 50
            M1021 P1 S      ; Disable maximum for sensor 1
            M1021 P1        ; Disable maximum for sensor 1
        """

        if len(args) > 2:
            return False

        new_maximum = None
        sensor_id = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['P', 'S']:
                continue

            if parameter == 'P' and len(value):
                sensor_id = int(value)
            elif parameter == 'S' and len(value):
                new_maximum = value

        if sensor_id is None:
            return False

        sensor = getattr(self, self.__sensor_map[sensor_id], False)
        sensor.maximum = new_maximum

        return True


    def __M1022(self, args: list) -> bool:

        """M1022 - Set sensor offset

        *Command syntax*

        ``M1022 P<sensor id> S<offset>``

        .. code-block:: none
            :linenos:
            M1022 P1 S10    ; Set offset for sensor 1 to 10
        """

        if len(args) != 2:
            return False

        new_offset = None
        sensor_id = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['P', 'S']:
                continue

            if parameter == 'P' and len(value):
                sensor_id = int(value)
            elif parameter == 'S' and len(value):
                new_offset = value

        if sensor_id is None or new_offset is None:
            return False

        sensor = getattr(self, self.__sensor_map[sensor_id], False)
        sensor.offset = new_offset

        return True

    def __M1023(self, args: list) -> bool:

        """M1023 - Set sensor coefficient

        *Command syntax*

        ``M1023 P<sensor id> S<coefficient>``

        .. code-block:: none
            :linenos:
            M1023 P1 S2.5    ; Set coefficient for sensor 1 to 2.5
        """

        if len(args) != 2:
            return False

        new_coefficient = None
        sensor_id = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['P', 'S']:
                continue

            if parameter == 'P' and len(value):
                sensor_id = int(value)
            elif parameter == 'S' and len(value):
                new_coefficient = value

        if sensor_id is None or new_coefficient is None:
            return False

        sensor = getattr(self, self.__sensor_map[sensor_id], False)
        sensor.coefficient = new_coefficient

        return True

    def __M1024(self, args: list) -> bool:

        """M1024 - Set sensor fallback value

        *Command syntax*

        ``M1024 P<sensor id> S<fallback>``

        .. code-block:: none
            :linenos:
            M1024 P1 S0    ; Set fallback for sensor 1 to 2.5
        """

        if len(args) != 2:
            return False

        new_fallback = None
        sensor_id = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['P', 'S']:
                continue

            if parameter == 'P' and len(value):
                sensor_id = int(value)
            elif parameter == 'S' and len(value):
                new_fallback = value

        if sensor_id is None:
            return False

        sensor = getattr(self, self.__sensor_map[sensor_id], False)
        sensor.fallback = new_fallback

        return True

    def __M1030(self, args: list) -> bool:
        """Set the heater RF state"""

        if len(args) != 1 or args[0][0] != 'P':
            return False

        try:
            value = int(args[0][1:])
        except ValueError:
            self.__logger.error(f'Cannot parse {args} for M1030')
            return False

        if value in [0, 1]:
            self.heater.rf = value
            return True
        else:
            self.__logger.error('Parameter P for M1030 must be 0 or 1')

    def __M1031(self, args: list) -> bool:
        """Set the heater mode"""

        if len(args) != 1 or args[0][0] != 'P':
            return False

        try:
            value = int(args[0][1:])
        except ValueError:
            self.__logger.error(f'Cannot parse {args} for M1031')
            return False

        modes = ['PWM', 'CW']

        if value in range(len(modes)):
            self.heater.mode = modes[value]
            return True
        else:
            self.__logger.error(f'Parameter P for M1030 must be in {modes}')

    def __M1032(self, args: list) -> bool:
        """Set the PWM Power"""

        if len(args) != 1 or args[0][0] != 'P':
            return False

        try:
            value = float(args[0][1:])
        except ValueError:
            self.__logger.error(f'Cannot parse {args} for M1032')
            return False

        if value > 0:
            self.heater.pwm_power = value
            return True
        else:
            self.__logger.error(f'Parameter P for M1032 must be > 0')

    def __M1033(self, args: list) -> bool:
        """Set the PWM pulse duration"""

        if not len(args):
            return False

        id = 0
        duration = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            if parameter == 'P':
                id = int(value)
            elif parameter == 'S':
                duration = float(value)

        if duration is None:
            self.__logger.error('Missing S<duration> for M1033')
            return False

        if id not in [0, 1, 2]:
            self.__logger.error('Paramater P<id> must be 0, 1 or 2 for M1033')

        if id == 0:
            self.heater.pwm_period = duration
        elif id == 1:
            self.heater.pwm_period_minimum = None if duration == '' else duration
        elif id == 2:
            self.heater.pwm_period_maximum = None if duration == '' else duration

        return True

    def __M1034(self, args: list) -> bool:
        """Set the PWM pulse duration"""

        if not len(args):
            return False

        id = 0
        duration = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            if parameter == 'P':
                id = int(value)
            elif parameter == 'S':
                duration = float(value)

        if duration is None:
            self.__logger.error('Missing S<duration> for M1034')
            return False

        if id not in [0, 1, 2]:
            self.__logger.error('Paramater P<id> must be 0, 1 or 2 for M1034')

        if id == 0:
            self.heater.ontime = duration
        elif id == 1:
            self.heater.ontime_min = None if duration == '' else duration
        elif id == 2:
            self.heater.ontime_max = None if duration == '' else duration

        return True

    def __M1035(self, args: list) -> bool:
        """Set the PWM pulse duration"""

        if not len(args):
            return False

        id = 0
        duration = None

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:
            if parameter == 'P':
                id = int(value)
            elif parameter == 'S':
                duration = float(value)

        if duration is None:
            self.__logger.error('Missing S<duration> for M1035')
            return False

        if id not in [0, 1, 2]:
            self.__logger.error('Paramater P<id> must be 0, 1 or 2 for M1035')

        if id == 0:
            self.heater.offtime = duration
        elif id == 1:
            self.heater.offtime_minimum = None if duration == '' else duration
        elif id == 2:
            self.heater.offtime_maximum = None if duration == '' else duration

        return True

    def __M1036(self, args: list) -> bool:

        """Set power minimum, maximum, value and step"""

        raise NotImplementedError

        if not len(args):
            return False

        id = 0

        parameters = self.__parse_parameters(args)

    def __M1037(self, args: list) -> bool:

        raise NotImplementedError

    def __M1038(self, args: list) -> bool:

        raise NotImplementedError

    def __M1039(self, args: list) -> bool:

        raise NotImplementedError

    def __parse_parameters(self, args: list, parameters: dict = None) -> bool:

        if parameters is None:
            parameters = [
                {'key': 'P', 'default': 0, 'value': None, 'required': False, 'type': int},
                {'key': 'S', 'default': None, 'value': None, 'required': True, 'type': float}
            ]

        for source_key, source_value in [(arg[0], arg[1:]) for arg in args]:
            for parameter in parameters:
                if source_key == parameter['key']:

                    if not len(source_value) and parameter['required']:
                        raise MCODERequiredParameterMissingException

                    try:
                        parameter['value'] = parameter['type'](source_value)
                    except ValueError:
                        return False
                    except TypeError:
                        return False

        return parameters

    def __set_temperature(self, args: list) -> bool:  # Set the RF status
    # TODO:
        """Set the temperature

        See documentation of the MCODE
        """
        if not (0 < len(args) <= 3):  # Do nothing if no arguments are supplied.
            return False

        for parameter, value in [(arg[0], arg[1:]) for arg in args]:

            if parameter not in ['B', 'F', 'I', 'S', 'T']:
                # Check if all supplied arguments are allowed
                raise MCODEUnkownParameterError

            if not len(value):
                return False

            try:
                value = float(value)
            except ValueError:
                raise MCODEParameterError
            except Exception:
                raise MCODEException

            if parameter == 'S':  # Perfom the action for the parameter RF
                self.temperature.pid_target = value

        return True

    def __set_temperature_unit(self, args: list) -> bool:
        # TODO:

        """See M149 documentation

        :param args: Variable list of arguments for M149, e.g. ``['C']``
        :type args: list
        :return: ``False`` if MCODE has no arguments, ``True`` otherwise
        :rtype: bool
        :raises: ``MCODEParameterError``, ``MCODEUnkownParameterError``

        *MCODE syntax*
        ``M149 <C|K|F>``

        *MCODE Example*
        ``M149 K ; Set the temperatur unit to Kelvin``

        """

        if len(args) != 1:
            return False

        parameter, value = args[0][:1], args[0][1:]

        if parameter not in self.unit_temperature_valid:
            raise MCODEUnkownParameterError

        if len(value):
            return False

        self.__logger.info(f'Set temperature unit to {parameter}')
        self.unit_temperature = parameter

        return True

    def __set_hf_lock(self, args: list) -> bool:
        ## TODO: remove
        """TODO

        *MCODE Syntax*
        ``Mxxx LOCK<0|1>``

        *MCODE Examples*
        - ``Mxxx LOCK0  ; Unlock the device``
        - ``Mxxx LOCK1  ; Lock the device``
        """

        if len(args) != 1:
            return False

        parameter, value = args[0][:4], args[0][4:]

        if parameter != 'LOCK':
            raise MCODEUnkownParameterError

        if len(value) != 1:
            return False

        try:
            value = bool(value)
        except ValueError:
            raise MCODEValueError

        if value:
            self.heater.lock()
        else:
            self.heater.unlock()

    def __set_hf_connection(self, args: list) -> bool:
        # TODO: remove / change
        """ TODO

        *MCODE syntax*
        ``M... [HOST<IPv4|IPv6|localhost>] [PORT<int>]``

        *MCODE examples*
        - ``M... HOST::1 PORT5025       ; Microwave has IP ::1 and port 5025``
        - ``M... HOSTlocalhost PORT1234 ; Microwave has DNS localhost and port 1234``
        """

        if not (0 < len(args) <= 2):
            return False

        for parameter, value in [(arg[:4], arg[4:]) for arg in args]:

            if parameter not in ['HOST', 'PORT']:
                raise MCODEUnkownParameterError

            if not len(value):
                return False

            if parameter == 'HOST':

                try:
                    self.heater.host = value
                except ValueError:
                    raise MCODEValueError

            elif parameter == 'PORT':

                try:
                    self.heater.port = int(value)
                except ValueError:
                    raise MCODEValueError

        if self.heater.is_available:
            self.__logger.info('HF connection successfull')
        else:
            self.__logger.warning('HF connection failed')

        return True

    def __set_hf_temperature_limits(self, args: list) -> bool:
        # TODO: remove, replaced by M1037
        """ TODO

        *MCODE syntax*
        ``M... [MIN<float, temperature>] [MAX<float, temperature>]``
        """

        if not (0 < len(args) <= 2):
            return False

        for parameter, value in [(arg[:3], arg[3:]) for arg in args]:

            if parameter not in ['MIN', 'MAX']:
                raise MCODEUnkownParameterError

            try:
                value = float(value) if value != '' else None
            except ValueError:
                raise MCODEValueError

            if parameter == 'MIN':
                self.__logger.info(f'Set minimum HF temperature to {value}')
                self.heater.temperature_min = value
            elif parameter == 'MAX':
                self.__logger.info(f'Set maximum HF temperature to {value}')
                self.heater.temperature_max = value

        return True

    def __set_hf_active(self, args: list) -> bool:
        # TODO: rewrite
        """ TODO
        """

        if len(args) != 1:
            return False

        parameter, value = args[0][:6], args[0][6:]

        if parameter != 'ACTIVE':
            raise MCODEUnkownParameterError

        if len(value) != 1:
            return False

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value not in [0, 1]:
            raise MCODEValueError

        self.heater.active = value
        self.__logger.info(f'Set HF active to {value}')
        return True

    def __set_hf_rf(self, args: list) -> bool:  # Set the RF status
        # TODO: replaced by M1030
        """Set the RF status

        :param args: Variable list of arguments for M400, e.g. ``['RF0']``
        :type args: list
        :return: ``False`` if MCODE has no arguments, ``True`` otherwise
        :rtype: bool
        :raises: ``MCODEParameterError``, ``MCODEUnkownParameterError``

        *MCODE syntax*
        ``M... RF<0|1>``

        *MCODE examples*
        - ``M... RF0 ; Disable microwave output``
        - ``M... RF1 ; Enable microwave output``
        """

        if len(args) != 1:
            return False

        parameter, value = args[0][:2], args[0][2:]

        if parameter != 'RF':
            raise MCODEUnkownParameterError

        if len(value) != 1:
            return False

        try:
            value = int(float(value))
        except ValueError:
            value = -1

        if value not in [0, 1]:
            raise ValueError

        self.heater.rf = value
        self.__logger.info(f'Set HF RF to {value}')
        return True

    def __set_hf_ontime_limits(self, args: list) -> bool:  # Set minimum and maximum ontime
        # # TODO: replaced by M1034
        """Set minimum and maximum ontime in nanoseconds

        :param args: Variable list of arguments for this MCODE, e.g.: ``['MIN100', 'MAX200']``
        :type args: list
        :return: ``False`` if parameter formatting is valid, ``True`` otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... [MIN[int, time in ns]] [MAX[int, time in ns]]``

        .. note::
            Float values will be parsed as int (floor) and set to None if negative.

        *MCODE usage examples*
        - ``M... MIN10000  ; Set the minimum ontime to 10.000ns``
        - ``M... MAX100000 ; Set the maximum ontime to 100.000ns``
        - ``M... MIN MAX   ; Disable minimum and maximum ontime (set to None)``

        """

        if not (0 < len(args) <= 3):
            return False

        for parameter, value in [(arg[:3], arg[3:]) for arg in args]:

            if parameter not in ['MIN', 'MAX', 'VAL']:
                raise MCODEUnkownParameterError

            if not len(value):
                value = -1

            try:
                value = float(value)
            except ValueError:
                raise MCODEParameterError

            if parameter == 'MIN':
                value = value if value > 0 else None
                self.heater.ontime_min = value
                self.__logger.info(f'Set ontime minimum to {value}')
            elif parameter == 'MAX':
                value = value if value > 0 else None
                self.heater.ontime_max = value
                self.__logger.info(f'Set ontime maximum to {value}')
            elif parameter == 'VAL':
                if value > 0:
                    self.heater.ontime = value

        return True

    def __set_hf_offtime(self, args: list) -> bool:  # Set offtime in ns
        # TODO: replaced by M1035
        """Set the offtime in ns

        :param args: Variable list of arguments for M..., e.g. ``['OFFT100']``
        :type args: list
        :return: ``False`` if MCODE has no arguments, ``True`` otherwise
        :rtype: bool
        :raises: ``MCODEParameterError``, ``MCODEUnkownParameterError``

        *Usage*
        ``M... OFFT<float, time in ns>``

        *Examples*
        - ``M... OFFT10000 ; Set the offtime to 10.000ns``

        """
        # Match the number of allowed parameters

        if len(args) != 1:
            return False

        parameter, value = args[0][:4], args[0][4:]
        # Check if the current parameter is allowed

        if parameter != 'OFFT':
            raise MCODEUnkownParameterError

        if not len(value):  # Value is mandatory and can't be remapped
            return False

        try:  # Check value type (float)
            value = float(value)
        except ValueError:
            raise MCODEParameterError

        # Check allwed value range (must be positive)
        if value <= 0:
            raise MCODETimeError('Offtime must be larger than 0')

        self.heater.offtime = value

        return True

    def __set_hf_power_limits(self, args: list) -> bool:  # Set minium and maximum power
        # TODO replaced by M1036
        """Set the minimum and maximum power in Watts [W]

        :param args: Variable list of arguments for M..., e.g. ``['MIN10', 'MAX20']``
        :type args: list
        :return: ``False`` if MCODE has no arguments, ``True`` otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... [MIN[float, power in W]] [MAX[float, power in W]]``

        .. note::
            Float values will be parsed as int (floor) and set to 0 if negative.

        *MCODE usage examples*
        - ``M... MIN10   ; Set the minimum power to 10W``
        - ``M... MAX50   ; Set the maximum power to 50W``
        - ``M... MIN MAX ; Disable minimum and maximum power (set to None)``
        """
        # Match the number of allowed parameters

        if not (0 < len(args) <= 3):
            return False

        for parameter, value in [(arg[:3], arg[3:]) for arg in args]:
            # Check if the current parameter is allowed
            if parameter not in ['MIN', 'MAX', 'VAL']:
                raise MCODEUnkownParameterError
            # Check value type (float), remap to None if empty, else clamp to >= 0

            if not len(value):
                return False

            try:
                value = float(value)
            except ValueError:
                raise MCODEParameterError

            if parameter == 'MIN':
                self.heater.power_min = value if value > 0 else None
            elif parameter == 'MAX':
                self.heater.power_max = value if value > 0 else None
            elif parameter == 'VAL':
                self.heater.power = value

        return True

    def __set_hf_power_step(self, args: list) -> bool:  # Set the power step
        # TODO: replaced by M1036
        """Set power step in Watts [W]

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... STEP<power in W>``

        *MCODE usage examples*
        - ``M... STEP5.0`` Set the power step to 5.0W
        - ``M... STEP0`` Disable the power step

        """
        # Match the number of allowed parameters

        if len(args) != 1:
            return False

        parameter, value = args[0][:4], args[0][4:]

        if parameter != 'STEP':
            raise MCODEUnkownParameterError

        if not len(value):
            return False

        try:
            value = float(value)
        except ValueError:
            raise MCODEParameterError

        self.heater.power_step = value if value > 0 else 0

        return True

    def __set_hf_frequency(self, args: list) -> bool:  # Set the frequency
        # TODO: replaced by M1035
        """Set frequency in 10kHertz [10kHz]

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... FREQ<frequency in 10kHz>``

        *MCODE usage examples*
        - ``M... FREQ2450000`` Set the frequency to 245000Hz = 2,45GHz

        """
        # Match the number of allowed parameters

        if len(args) != 1:
            return False

        parameter, value = args[0][:4], args[0][4:]

        if parameter != 'FREQ':
            raise MCODEUnkownParameterError

        if not len(value):
            return False

        try:
            value = float(value)
        except ValueError:
            raise MCODEParameterError

        if value <= 0:
            raise MCODENegativeError('Frequency cannot be smaller than 0')

        self.heater.frequency = max(value, 0)

        return True

    def __set_hf_mode(self, args: list) -> bool:  # Set the frequency
        # TODO: replaced by M1031
        """Set operation mode

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... MODE<mode code>``

        *Examples*
        - ``M... MODEPWM`` Set the mode to PWM

        """
        # Match the number of allowed parameters

        if len(args) != 1:
            return False

        parameter, value = args[0][:4], args[0][4:]

        if parameter != 'MODE':
            raise MCODEUnkownParameterError

        if not len(value):
            return False

        try:
            value = str(value)
        except ValueError:
            value = ''

        if value not in ['PWM', 'CW', 'NWA', 'PWM-NWA']:
            raise MCODEParameterError

        self.heater.mode = value

        return True

    def __set_temperature_limits(self, args: list) -> bool:  # Set the minium and maximum temperature
        """Set minimum and maximum temperature in degree Celcius [°C]

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        .. note::
            Set the temperature to -300°C (impossible value) or any value below the absolute
            temperature zero to disable these limits.

        *MCODE syntax*
        ``M... [MIN<float, temperature>] [MAX<float, temperature>]``

        *MCODE Usage examples*
        - ``M... MIN100`` Set the minimum temperature to 100°C
        - ``M... MAX300`` Set the maximum temperature to 300°C
        - ``M... MIN MAX`` Disable minimum and maximum temperature (set to None)

        """

        ABS_ZERO = -273.15

        if not (0 < len(args) <= 2):  # Do nothing if no arguments are supplied.
            return False

        for parameter, value in [(arg[:3], arg[3:]) for arg in args]:

            if parameter not in ['MIN', 'MAX']:  # Check if all supplied arguments are allowed
                raise MCODEUnkownParameterError

            try:  # Check if value is of the right type (here: int)
                value = float(value) if value != '' else None
            except ValueError:
                raise MCODEFloatError

            if value is not None:
                value = max(value, ABS_ZERO) if value >= ABS_ZERO else None

            if parameter == 'MIN':
                self.temperature.target_minimum = value
            elif parameter == 'MAX':
                self.temperature.target_maximum = value

        return True

    def __set_pid_terms(self, args: list) -> bool:  # set the PID values

        """Set the parameters PID for the PID-Controller

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... [P<float, value] [I<float, value>] [I<float, value>]``

        *MCODE usage examples*
        - ``M... P100 ; Set the value of P to 100``
        - ``M... I50 D2 ; Set the values I and D to 50 and 2``
        - ``M... P1 I1 D1 ; Set the value P, I, D to 1, 1, 1``

        """

        if not (0 < len(args) <= 3):  # Do nothing if no arguments are supplied.
            return False

        for parameter, value in [(arg[:1], arg[1:]) for arg in args]:

            if parameter not in ['P', 'I', 'D']:  # Check if all supplied arguments are allowed
                raise MCODEUnkownParameterError

            if not len(value):
                return False

            try:  # Check if value is of the right type (here: int)
                value = float(value)
            except ValueError:  # Ignore if value is not set
                raise MCODEParameterError

            if parameter == 'P':
                self.temperature.Kp = value
            elif parameter == 'I':
                self.temperature.Ki = value
            elif parameter == 'D':
                self.temperature.Kd = value

        return True

    def __set_pid_limits(self, args: list) -> bool:  # Set the minimum and maximum PID output

        """Set minimum and maximum PID outputs

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEParameterError

        *MCODE syntax*
        ``M... [MIN<float, output value>] [MAX<float, output value>]``

        *MCODE usage examples*
        - ``M... MIN-50 ; Set the minimum output to -50``
        - ``M... MAX10 ; Set the maximum output to 10``
        - ``M... MIN MAX ; Disable minimum and maximum output (set to None)``

        """

        if not (0 < len(args) <= 2):  # Do nothing if no arguments are supplied.
            return False

        for parameter, value in [(arg[:3], arg[3:]) for arg in args]:

            if parameter not in ['MIN', 'MAX']:  # Check if all supplied arguments are allowed
                raise MCODEUnkownParameterError

            try:  # Check if value is of the right type (here: float)
                value = float(value) if value != '' else None
            except ValueError:  # If there's no value, disable with None
                raise MCODEParameterError

            if parameter == 'MIN':
                self.temperature.control_min = value
            elif parameter == 'MAX':
                self.temperature.control_max = value

        return True

    def __set_pid_sample_time(self, args: list) -> bool:  # Set the PID sample time
        # TODO: rewrite
        """Set the sample time in seconds [s]

        :param args: Variable list of arguments for M...
        :type args: list
        :return: False if MCODE has no arguments, True otherwise
        :rtype: bool
        :raises: MCODEFloatError, MCODETimeError, MCODEUnkownParameterError

        *MCODE syntax*
        ``M... SAMPLE<float, time in s>``

        *MCODE usage example*
        - ``M... SAMPLE0.001 ; Set the sample time to 0,001s = 1ms``

        """

        if len(args) != 1:  # Do nothing if no arguments are supplied.
            return False

        parameter, value = args[0][:6], args[0][6:]

        if parameter != 'SAMPLE':
            raise MCODEUnkownParameterError

        if not len(value):  # Check if allowed arguments have a value
            return False

        try:  # Check if value is of the right type (here: float)
            value = float(value)
        except ValueError:
            raise MCODEFloatError

        if value <= 0:  # Check that frequency is not below 0
            raise MCODETimeError

        self.temperature.pid.sample_time = value

        return True


class MCODEException(Exception):
    """Base class for MCODE exceptions"""
    def __init__(self, *args, **kwargs):
        self.message = args[0] if args else 'No message available'
        self.logger = kwargs.get('logger', False)
        if self.logger and self.message:
            self.logger.warning(self.message)


class RequiredParameterMissingException(MCODEException):
    pass


class HeaterMCODEException(MCODEException):
    pass


class UnsupportedMCODEException(MCODEException):
    pass


class MCODEParameterError(MCODEException):
    pass


class MCODEUnkownParameterError(MCODEParameterError):
    pass


class MCODEValueError(MCODEParameterError):
    pass


class MCODEFloatError(MCODEValueError):
    pass


class MCODETimeError(MCODEValueError):
    pass


class MCODENegativeError(MCODEValueError):
    pass
