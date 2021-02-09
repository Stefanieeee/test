class HTTPMixin(BaseController):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._flask_start()


"""http的网页上获取实时的数值
"""






    def _flask_route_add(self):
        """HTTP Endpoint for fetching live values

        **Available Endpoints**

        +------------------------------+----------------------------------------+
        | Path                         | Description                            |
        +==============================+========================================+
        | /live/heater/pwm/power       | Curret PWM RF power                    |
        +------------------------------+----------------------------------------+
        | /live/heater/power/output    | Output power (float) [W]               |
        +------------------------------+----------------------------------------+
        | /live/heater/power/reflected | Reflected power (float) [W]            |
        +------------------------------+----------------------------------------+
        | /live/heater/power/forward   | Curret PWM RF power (float) [W]        |
        +------------------------------+----------------------------------------+
        | /live/heater/pwm/power       | Curret PWM RF power                    |
        +------------------------------+----------------------------------------+
        | /live/temperature/current    | Temperature                            |
        +------------------------------+----------------------------------------+
        | /live/temperature/target     | Temperature target                     |
        +------------------------------+----------------------------------------+
        | /live/pid/control            | PID control output                     |
        +------------------------------+----------------------------------------+
        """
        super()._flask_route_add()

        @self._flask.route('/live/heater/pwm/power')
        def _flask_heater_pwm_power():

            return str(self.heater.pwm_power)

        @self._flask.route('/live/heater/temperature')
        def _flask_heater_temperature():

            return str(self.heater.temperature)

        @self._flask.route('/live/temperature/current')
        def _flask_temperature_current():

            return str(self.temperature.current)

        @self._flask.route('/live/temperature/target')
        def _flask_temperature_target():

            return str(self.temperature.pid_target)

        @self._flask.route('/live/pid/control')
        def _flask_pid_control():

            return str(self.temperature.pid_control)
