# coding=utf-8
from __future__ import absolute_import
from octoprint.util import RepeatedTimer
import mwcontrol
import logging
import flask
import io
import queue
import octoprint.plugin

class IHM3DPrinter(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SimpleApiPlugin,
                   octoprint.plugin.ShutdownPlugin,
                   octoprint.plugin.EventHandlerPlugin):

    def on_after_startup(self):

        """ Hook from octoprint.plugin.StartupPlugin"""

        data_dir = self.get_plugin_data_folder()
        self.nozzlecontrol = mwcontrol.NozzleControl(data_dir=data_dir)
        self.gcode_queue = queue.SimpleQueue()
        RepeatedTimer(0.1, self.main_loop).start()
        RepeatedTimer(1, self.log_loop).start()
        RepeatedTimer(0.05, self.gcode_loop).start()

    def log_loop(self):

        """Loop for web log viewer"""

        while not self.nozzlecontrol.logger_queue.empty():

            record = self.nozzlecontrol.logger_queue.get()
            self._plugin_manager.send_plugin_message(f'{self._identifier}_logger', record.getMessage())

    def gcode_loop(self):

        """GCODE processing loop"""

        while not self.gcode_queue.empty():
            cmd = self.gcode_queue.get()
            self.nozzlecontrol.onGCODE(cmd)

    def main_loop(self):

        """ Main control loop"""

        self.nozzlecontrol.control()
        self.nozzlecontrol.datalogger_collect()
        message = self.nozzlecontrol.datalogger_current.copy()
        self._plugin_manager.send_plugin_message(self._identifier, message)
        self._plugin_manager.send_plugin_message(f'{self._identifier}_datalogger', self.nozzlecontrol.datalogger_status)

    def on_api_get(self, request):

        """ Hook from octoprint.plugin.SimpleApiPlugin"""

        if 'download_datalog' in request.args:
            filename = request.args['download_datalog']

            try:
                file = self.nozzlecontrol.datalogger_files[filename]
            except KeyError:
                return f'Could not find {filename}'

            buffer = io.BytesIO()
            buffer.write(file.data.encode(encoding='utf-8'))
            buffer.seek(0)

            return flask.send_file(
                buffer,
                as_attachment=True,
                attachment_filename=file.name,
                mimetype='text/csv'
            )

        if 'datalogger_current' in request.args:
            return flask.jsonify(**self.nozzlecontrol.datalogger_current)

        return flask.jsonify(status='error', message='Unsupported command')

    def on_api_command(self, command, data):

        api_error = lambda text: flask.jsonify(status='error', message=text)
        api_success = lambda text: flask.jsonify(status='success', message=text)
        response = api_error('Unsupported command')

        # Check that the MCS is available
        if not getattr(self, 'nozzlecontrol', False):
            response = api_error('MCS not available')

        if command == 'GCODE' and 'gcode_cmd' in data:
            gcode_cmd = data['gcode_cmd']
            self.gcode_queue.put(gcode_cmd)
            return api_success(f'Received GCODE command {gcode_cmd}')

        return response

    def get_api_commands(self):

        """List all available API commands"""

        return {
            'GCODE': ['gcode_cmd']
        }

    def on_shutdown(self):

        """Hook from octoprint.plugin.ShutdownPlugin"""

        self.nozzlecontrol.stop()

    def get_settings_defaults(self):

        """Hook from octoprint.plugin.SettingsPlugin"""

        return {}

    def get_template_configs(self):

        """Hook from octoprint.plugin.TemplatePlugin"""

        return [
            dict(type='tab',
                 name='Microwave Control System',
                 template='ihm_3dprinter_mcs_tab.jinja2',
                 replaces='temperature'),
        ]

    def get_assets(self):

        """Hook from octoprint.plugin.TemplatePlugin"""

        return dict(
            js=[
                'js/main.js',
                'js/utils.js',
                'js/viewmodels/CombinedViewModels.js',
                'js/viewmodels/FilamentSpeedViewModel.js',
                'js/viewmodels/HeaterTemperatureViewModel.js',
                'js/viewmodels/HeaterPowerForwardViewModel.js',
                'js/viewmodels/HeaterPowerReflectedViewModel.js',
                'js/viewmodels/HeaterConnectionViewModel.js',
                'js/viewmodels/HeaterStatusViewModel.js',
                'js/viewmodels/HeaterFrequencyViewModel.js',
                'js/viewmodels/HeaterPowerViewModel.js',
                'js/viewmodels/HeaterPWMViewModel.js',
                'js/viewmodels/HeaterTimingViewModel.js',
                'js/viewmodels/TemperaturePIDViewModel.js',
                'js/viewmodels/NozzleTemperatureViewModel.js',
                'js/viewmodels/PIDControlViewModel.js',
                'js/viewmodels/ModelControlViewModel.js',
                'js/viewmodels/MicrowaveControlViewModel.js',
                'js/viewmodels/MicrowavePowerSensorViewModel.js',
                'js/viewmodels/DataLoggerViewModel.js',
                'js/viewmodels/LoggerViewModel.js',
            ],
            css=['css/plugin.css']
        )

    # Hooks
    def gcode_callback(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):

        """ Hook from for GCODE communication layer

        Received commands are pushed into a threading queue so there is no processing time lost
        here. The parsing and processing of the GCODE commands must take place somewhere else.
        """

        if not getattr(self, 'nozzlecontrol', False):
            return None

        # Special command to catch the feedrate changes
        if gcode == 'G1':

            feedrate = self.nozzlecontrol.parseFeedrateFromGCODE(cmd)

            if feedrate is not None:
                action_cmd = f'M118 A1 action:feedrate_{feedrate}'
                self.gcode_queue.put(cmd)
                return [('M400', ), (action_cmd, ), (cmd, )]

        if gcode in self.nozzlecontrol.gcodes_pass:
            self.gcode_queue.put(cmd)
            return None # Do not alter the GCODE
        elif gcode in self.nozzlecontrol.gcodes_absorb:
            self.gcode_queue.put(cmd)
            return None, # Absorb the MCODE

    def action_callback(self, comm, line, action, *args, **kwargs):

        """Hook from for action commands from the printer

        Defin custom action commands to be implemented by this plugin
        """

        if not getattr(self, 'nozzlecontrol', False):
            return None

        self._logger.info(f'Receive action "{action}"')

        if action in ['cancel', 'pause', 'paused', 'disconnect']:
            self.nozzlecontrol.stop()
        elif action in ['pause', 'paused']:
            self.nozzlecontrol.pause()
        elif action in ['resume', 'resumed']:
            self.nozzlecontrol.resume()
        elif action.startswith('feedrate_'):
            self.nozzlecontrol.gcode_feedrate = float(action[9:])

    def atcommand_callback(self, comm, phase, command, parameters, tags=None, *args, **kwargs):

        """Hook for @commands from OctoPrint

        Define custon @-commands to be implemented by this plugin.

        """

        if command in ['cancel', 'abort']:
            self.nozzlecontrol.stop()
        elif command in ['pause']:
            self.nozzlecontrol.pause()
        elif command in ['resume']:
            self.nozzlecontrol.resume()

    def on_event(self, event, payload):
        pass


__plugin_name__ = "IHM 3DPrinter"
__plugin_pythoncompat__ = ">=3.6,<4" # only python 3.6 or higher

def __plugin_load__():

    global __plugin_implementation__
    global __plugin_hooks__
    __plugin_implementation__ = IHM3DPrinter()
    __plugin_hooks__ = {
        'octoprint.comm.protocol.gcode.queuing': __plugin_implementation__.gcode_callback,
        'octoprint.comm.protocol.atcommand.queuing': __plugin_implementation__.atcommand_callback,
        'octoprint.comm.protocol.action': __plugin_implementation__.action_callback,
    }
