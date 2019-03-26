import logging
from io import StringIO


class LogCapture(object):
    """ Class for temporarily capturing logs to a string

        Example usage:
            log_cap = LogCapture(logger)
            log_cap.start_capture(log_level=logging.DEBUG)
            # Do stuff
            print log_cap.stop_capture()

        Example usage:
            with LogCapture(logger, level=logging.DEBUG) as log_cap:
                # Do stuff
            print log_cap.last_logs
    """

    # TODO: write tests, think about states of log capture and make sure to
    # handle weird state changes (e.g. stop_capture >> stop_capture or
    # start_capture >> start_capture)

    def _init_buffer(self):
        self.log_buf = StringIO()
        # print >> self.log_buf, 'Captured log output:'
        # print('Captured log output:', file=self.log_buf)

    def _reset(self):
        # Remove handler
        self.logger.removeHandler(self.log_handler)
        self.log_handler.flush()

        # Restore old log level
        if self.old_log_level:
            self.logger.set_Level(self.old_log_level)
            self.old_log_level = None

        # Clean buffer
        self._init_buffer()

    def __init__(self, logger, level=None):
        """
            Args:
                logger (logging.Logger): logger to capture logs from
                level (int): log level override (ex. logging.DEBUG)
        """
        self._init_buffer()
        self.logger = logger
        self.log_handler = logging.StreamHandler(self.log_buf)
        self.log_level = level

    def start_capture(self, level=None):
        """ Start capturing logs

            Args:
                level (int): log level override (ex. logging.DEBUG)
        """
        if level or self.log_level:
            log_level = level or self.log_level
            self.old_log_level = self.logger.level
            self.logger.setLevel(log_level)

        self.logger.addHandler(self.log_handler)

    def stop_capture(self):
        """ Returns the captured logs and restores original logging config

            Returns:
                str: captured logs
        """
        self.log_buf.flush()
        self.last_logs = self.log_buf.getvalue()

        self._reset()
        return self.last_logs

    def __enter__(self):
        self.start_capture()
        return self

    def __exit__(self, type, value, traceback):
        self.stop_capture()

