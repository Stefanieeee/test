import socket
import threading
import sys
import errno
import time
import ipaddress
from mwcontrol.BaseController import BaseController

"""socket 应用程序通常通过"套接字"向网络发出请求或者应答网络请求，使主机间或者一台计算机上的进程间可以通讯

"""
class BindMixin:

    def __reconfigure(self):
        """TODO
        """

        super().__reconfigure()

        try:
            status = self.__bind_thread.is_alive()

        except AttributeError:
            pass

        else:
            if status:
                self.stop()
                self.bind()

    def bind(self, host=None, port=None):

        """TODO
        """

        host = host or self.connection_host
        port = port or self.connection_port
        self.__bind_socket = socket.socket()
        self.__bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__bind_socket.settimeout(self.connection_timeout)
        self.__bind_socket.bind((host, port))
        """绑定地址（host,port）到套接字
        """
        
        self.__bind_socket.listen(1)
        self.__start_bind_thread()

    def stop(self):
        """TODO
        """

        try:
            self.connection_stop_event.set()

        except AttributeError:  # No thread is running
            pass

        else:
            self.__bind_thread.join()

    def on_message(self, message, encoding='utf-8'):

        """Placeholder to be overwitten in child instances.

        :param message: Content of the message
        :type message: str
        :param encoding: Endoding of the message
        :type encoding: str, optional
        """

        self.message = message.decode(encoding)
        self.logger.debug(f'Receive "{self.message}"')

    def __start_bind_thread(self, daemon=False):

        """ TODO
        """

        self.connection_stop_event = threading.Event()
        self.__bind_thread = threading.Thread(target=self.__bind_loop)

        if daemon:
            self.logger.debug('Run bind thread as daemon')
            self.__bind_thread.setDaemon(True)

        self.__bind_thread.start()

    def __bind_loop(self):

        """TODO
        """

        self.logger.debug(f'Start listener for {self.__class__.__name__}')
        self.logger.debug(f'Bind to {self.connection_host}:{self.connection_port}')

        while not self.connection_stop_event.is_set():

            try:
                client, addr = self.__bind_socket.accept()
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(e)
                sys.exit(1)

            message = False

            while not message:

                try:
                    message = client.recv(self._settings['connection']['buffer'])
                except socket.error as e:

                    if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                        continue

                    self.logger.warn(e)
                    sys.exit(1)

                self.on_message(message)
                client.close()

        self.__bind_socket.close()
        self.logger.debug(f'Stop listener for {self.__class__.__name__}')


class ConnectMixin:

    def __reconfigure(self):

        pass

    def connect(self):

        """Connect a socket.

        """

        self.__connection_socket = None

        try:
            self.__connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            self.logger.error(f'Error {msg[0]}: {msg[1]}')
            sys.exit(1)
        else:
            self.__connection_socket.settimeout(self.connection_timeout)

        try:
            self.__connection_socket.connect((self.connection_host, self.connection_port))
        except socket.timeout:
            self.logger.error(f'Connection timeout: {self.connection_host}:{self.connection_port}')
            sys.exit(1)
        except socket.error:
            self.logger.error(f'Error connecting to {self.connection_host}:{self.connection_port}')
            sys.exit(1)

        self.logger.debug(f'Connected to {self.connection_host}:{self.connection_port}')

    def send_message(self, message, encoding='utf-8'):

        """Send a message through the socket

        :param message: Content of the message
        :type message: str
        :param encoding: Endoding of the message
        :type encoding: str, optional
        """

        if not len(message):
            return False

        self.connect()
        self.__connection_socket.sendall(str(message).encode(encoding))
        self.__connection_socket.close()

    def __send_loop(self):

        """Loop to send messages at a set interval
        """

        pass


class BaseConnectionHandler(BindMixin, ConnectMixin, BaseController):

    def __init__(self, *args, **kwargs):
        """args是一些入参的元组
           kwargs是传入的多个键值对key = value参数
        """

        super().__init__(*args, **kwargs)
        self.message = None

    def __del__(self):

        self.stop()

    def update_settings(self, settings={}):

        super().update_settings(settings=settings)

        if 'connection' not in self._settings:
            self._settings.update(BaseConnectionHandler.get_defaults())

    def __reconfigure(self):

        pass

    @classmethod
    def get_defaults(cls):

        """Get the default settings as a dict.

        :return: Dictionary with all default settings
        :rtype: dict
        """

        return {
            'connection': {
                'host': '0.0.0.0',
                'port': 2342,
                'timeout': 0.1,
                'encoding': 'utf-8',
                'buffer': 4096,
            },
            'name': cls.__name__
        }

    @property
    def status(self):

        # status = super().status
        status = {}
        status['connection'] = self._settings['connection']
        return status

    @property
    def host(self):

        return self._settings['connection']['host']

    @host.setter
    def host(self, value):

        if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            value = ipaddress.ip_address('127.0.0.1' if value == 'localhost' else value)

        self._settings['connection']['host'] = str(value)
        self.logger.debug(f'Set connection host to {self.host}')
        self.__reconfigure()

    @property
    def port(self):

        return self._settings['connection']['port']

    @port.setter
    def port(self, value):

        self._settings['connection']['port'] = int(value)
        self.logger.debug(f'Set connection port to {self.port}')
        self.__reconfigure()

    # Deprecated!

    @property
    def connection_host(self):

        self.logger.warning('.connection_host is deprecated. Use .host instead')
        return self._settings['connection']['host']

    @connection_host.setter
    def connection_host(self, value):

        self.logger.warning('.connection_host is deprecated. Use .host instead')

        if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            value = ipaddress.ip_address('127.0.0.1' if value == 'localhost' else value)

        self._settings['connection']['host'] = str(value)
        self.logger.debug(f'Set connection host to {self.connection_host}')
        self.__reconfigure()

    @property
    def connection_port(self):

        self.logger.warning('.connection_port is deprecated. Use .host instead')
        return self._settings['connection']['port']

    @connection_port.setter
    def connection_port(self, value):

        self.logger.warning('.connection_port is deprecated. Use .host instead')
        self._settings['connection']['port'] = int(value)
        self.logger.debug(f'Set connection port to {self.connection_port}')
        self.__reconfigure()

    @property
    def connection_name(self):

        return self._settings['name']

    @connection_name.setter
    def connection_name(self, value):

        self._settings['name'] = value
        self.__reconfigure()

    @property
    def connection_timeout(self):

        return self._settings['connection']['timeout']

    @connection_timeout.setter
    def connection_timeout(self, value):

        self._settings['connection']['timeout'] = round(float(value), 2)
        self.logger.debug(f'Set connection host to {self.connection_timeout}s')
        self.__reconfigure()

    def stop(self):
        """TODO
        """

        super().stop()

    def test(self, message='Hello World'):
        """TODO
        """

        self.bind()
        self.send_message(message)

        while self.message is None:
            time.sleep(0.1)

        self.stop()

        return True if self.message == message else False


class ExceptionBaseClass(Exception):

    def __init__(self, *args, **kwargs):

        self.message = args[0] if args else None
        self.logger = kwargs.get('logger', False)

    def __str__(self):

        if self.message:
            return 'Exception: {}'.format(self.message)
        else:
            return 'Exception raised. No message available'


class DeviceNotAvailableException(ExceptionBaseClass):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        if self.logger:
            self.logger.warning('Device is not available, return default value instead.')
