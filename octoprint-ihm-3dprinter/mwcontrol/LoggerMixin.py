import logging
import queue

"""输出运行日志
"""

class LoggerMixin:

    def __init__(self, *args, **kwargs):

        super().__init__()
        self.__configure(*args, **kwargs)

    @classmethod
    def get_defaults(cls):

        return {}

    def update_settings(self, settings={}, *args, **kwargs):

        self._settings = getattr(self, '_settings', LoggerMixin.get_defaults())

    def __configure(self, logger_name=None, logger_level='DEBUG', *args, **kwargs):

        """Get child of a given logger or setup standalone default logger

        """

        self.logger = logging.getLogger(logger_name)

        if logger_name not in logging.Logger.manager.loggerDict:  # Logger is not configures
            self.__configure_QueueHandler()

            if kwargs.get('log_console_enabled', True):
                self.__configure_StreamHandler()

        self.logger.setLevel(getattr(logging, logger_level))

    def __configure_StreamHandler(self):

        """Internal method to configure the StreamHandler for logging

        """

        if not (any(isinstance(handl, logging.StreamHandler) for handl in self.logger.handlers)):
            LOG_DATE_FORMAT = '%d-%b-%y %H:%M:%S'
            LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            self._streamhandler = logging.StreamHandler()
            _formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            self._streamhandler.setFormatter(_formatter)
            self.logger.addHandler(self._streamhandler)

    def __configure_QueueHandler(self):

        """Custom MCS (Microwave Control System) Handler logging class
        """
        LOG_DATE_FORMAT = '%d-%b-%y %H:%M:%S'
        LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.logger_queue = queue.SimpleQueue()
        queueHandler = logging.handlers.QueueHandler(self.logger_queue)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        queueHandler.setFormatter(formatter)
        self.logger.addHandler(queueHandler)

    # def logger_configure_FileHandler(self):
    #     pass

    def update_settings(self, *args, **kwargs):

        pass
