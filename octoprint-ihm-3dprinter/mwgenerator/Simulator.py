# coding=utf-8

import socket
import logging
import threading
import errno
import sys
import signal
import time
import random

"""模拟器
"""


def threaded(fn):

    def wrapper(*args, **kwargs):

        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        return thread

    return wrapper


class Simulator(object):

    """Emulate a HPG Microwave device

    :param host: Netword adresse to bind the listener to. Default is ``''``.
    :type host: str, optional
    :param port: Network port to bind the listener to. Default is ``5025``.
    :type port: int, optional
    :param timeout: Timeout in seconds for the listener. Default is ``0.1``
    :type timeout: int, optional
    :param logger: Use an existing logger to attached the child logger. Default is ``False``.
    :type client: class:`logging.Logger`
    """
    LOGLEVEL = 'DEBUG'

    def __init__(self, host='', port=5025, timeout=0.1, logger=False):

        """Class constructor.
        """
        self._configureLogger(logger)
        self.configure()
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.stopEvent = threading.Event()
        signal.signal(signal.SIGINT, self.quit)
        self.listen()

    def _configureLogger(self, logger=False, name=False, level=False):

        """Get child of a given logger or setup standalone default logger

        :param logger: Use an existing logger to attached the child logger.
        :type client: class:`logging.Logger`
        :param name: Set a specific name for the child logger. Defaults to ``__class__.__name__``
        :type name: str, optional
        :param level: Set the loglevel for the child logger. Defaults to :attr:`Simulator.LOGLEVEL`
        :type level: str, optional
        """

        name = name or self.__class__.__name__
        level = level or self.__class__.LOGLEVEL

        if logger:
            self.logger = logger.getChild(name)
            self.logger.setLevel(getattr(logging, level))

        else:
            logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                datefmt='%d-%b-%y %H:%M:%S', level=getattr(logging, level)
            )
            self.logger = logging.getLogger(name)
            self.logger.warn('No logger set, using standalone logger instead')

        self.logger.debug('Loglevel set to {}'.format(level))

    def configure(self):

        """Set the default values and callbacks.
        """

        self.id = 'HBH Microwave,E128,20181120,0001'
        self.FREQuency = 0  # 245000
        self.POWer = 0  # 1
        self.RF = 0
        self.OFFtime = 0  # 10000
        self.ONtime = 0  # 100
        self.temperature = 42.23
        self.MODe = 'CW'
        self.callbacks = {
            '*IDN?': lambda: self.id,
            'CONF:MOD': lambda *args: self.set_mode(value=args[0]),
            'CONF:MOD?': lambda *args: self.MODe,
            'CONF:FREQ': lambda *args: self.set_frequency(value=args[0]),
            'CONF:FREQ?': lambda *args: str(self.FREQuency),
            'CONF:POW': lambda *args: self.set_power(value=args[0]),
            'CONF:POW?': lambda *args: str(self.POWer),
            'CONT:RF': lambda *args: self.set_rf(value=args[0]),
            'CONT:RF?': lambda *args: str(self.RF),
            'CONF:PWM:OFF': lambda *args: self.set_pwm_offtime(value=args[0]),
            'CONF:PWM:OFF?': lambda *args: str(self.OFFtime),
            'CONF:PWM:ON': lambda *args: self.set_pwm_ontime(value=args[0]),
            'CONF:PWM:ON?': lambda *args: str(self.ONtime),
            'SENSe:TEMPerature?': lambda *args: str(round(random.uniform(20, 40), 2)),
            'SENSe:POWer:FORward?': lambda *args: str(round(random.uniform(0, 10), 2)),
            'SENSe:POWer:REFLect?': lambda *args: str(round(random.uniform(0, 10), 2))
        }

    def set_mode(self, value):

        """Set the operation mode.

        :param value: The operation mode to be set.
        :type value: str

        .. note::
            Valid operation modes are `CW`, `PWM`, `NWA` and `PWM-NWA`. All other values are
            ignored.
        """

        try:
            value = str(value)

        except ValueError:
            value = ''

        if value in ['CW', 'PWM', 'NWA', 'NWA-PWM']:
            self.MODe = value
            self.logger.debug('MODe set to {}'.format(self.MODe))

    def set_frequency(self, value):

        """Set the output frequency in multiples of 10kHz.

        :param value: The output frequency to be set in multiples of 10kHz.
        :type value: str
        """

        try:
            value = int(value)

        except ValueError:
            value = -1

        if value > 0:
            self.FREQuency = value
            self.logger.debug('Frequency set to {}'.format(self.FREQuency))

    def set_power(self, value):
        """Set the output power in multiples of 10W.

        :param value: The output power to be set in multiples of 10W.
        :type value: str
        """

        try:
            value = float(value)

        except ValueError:
            value = -1

        if value > 0:
            self.POWer = value
            self.logger.debug('Power set to {}'.format(self.POWer))

    def set_rf(self, value):

        """Enable or disable the output.

        :param value: Enable with `1` and disable with `0`
        :type value: str
        """

        try:
            value = int(value)

        except ValueError:
            value = -1

        if value in [0, 1]:
            self.RF = value
            self.logger.debug('RF set to {}'.format(self.RF))

    def set_pwm_ontime(self, value):

        """Set the PWM ontime in nanoseconds.

        :param value: The PWM ontime to be set in nanoseconds.
        :type value: str
        """

        try:
            value = int(value)

        except ValueError:
            value = -1

        if value > 0:
            self.ONtime = value
            self.logger.debug('PWM ontime set to {}'.format(self.ONtime))

    def set_pwm_offtime(self, value):

        """Set the PWM offtime in nanoseconds.

        :param value: The PWM offtime to be set in nanoseconds.
        :type value: str
        """

        try:
            value = int(value)

        except ValueError:
            value = -1

        if value > 0:
            self.OFFtime = value
            self.logger.debug('PWM offtime set to {}'.format(self.OFFtime))

    def handle_message(self, message, encoding='utf-8'):

        """Decode and handle incoming messages.

        :param message: The messaage to be processed.
        :type message: str
        :param encoding: Decode the message with this encoding. Default is `utf-8`.
        :type encoding: str, optional
        """

        message = message.decode(encoding).rstrip('\r\n')
        self.logger.debug('Received message {}'.format(message))
        data = message.split(' ')
        arguments = data[1:] if len(data) > 1 else []

        if data[0] in self.callbacks:

            result = self.callbacks[data[0]](*arguments) or False
            self.send_message(result) if result else None
            return

        self.logger.error('Unknown command: {}'.format(message))

    def send_message(self, message, encoding='utf8'):

        """Format and send message through the socket

        :param message: The messaage to be sent.
        :type message: str
        :param encoding: Encode the message with this encoding. Default is `utf-8`.
        :type encoding: str, optional
        """

        self.logger.debug('Sending response {}'.format(message))
        self.client.sendall(message.encode(encoding))

    def stop(self):

        """Stop the listener and close the socket.

        """

        self.stopEvent.set()
        self.s.close()

    def quit(self, *args):

        self.stop()
        time.sleep(1)
        sys.exit(0)

    @threaded
    def listen(self):

        """Listen for connections in a thread

        Incoming messages are handled with handle_message(msg)
        """

        self.s.listen(1)
        self.logger.info('Listen on {}:{}'.format(self.host, self.port))

        while not self.stopEvent.is_set():
            data = False

            try:
                self.client, addr = self.s.accept()

            except socket.timeout:
                continue

            while not data:

                try:
                    data = self.client.recv(1024)

                except socket.error as e:

                    if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                        continue

                    self.logger.warn(e)
                    sys.exit(1)

                self.handle_message(data)
                self.client.close()

        self.logger.info('Stop signal received for listener')
