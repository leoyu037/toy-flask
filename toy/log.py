import datetime
import json
import logging
import sys
import traceback

from ddtrace.helpers import get_correlation_ids


def _format_datadog_log(level, message, logger='not_set', extra_fields=None, err=None):
    """All the fields set here are special Datadog attributes (except for
    'compass')"""
    record = {
        'time': datetime.datetime.now().isoformat(),
        'status': level,
        'message': message,
        # 'service': 'not_set',
    }

    record['logger'] = {
        'name': logger,
        'thread_name': 'not_set',
    }

    trace_id, span_id = get_correlation_ids()
    record['dd'] = {
        'trace_id': trace_id or 0,
        'span_id': span_id or 0,
    }

    if err:
        record['error'] = {
            'kind': err.__class__.__name__,
            # Apparently err.message doesn't exist in Python 3
            'message': err.__str__(),
            'stack': traceback.format_exc(),
        }

    if extra_fields:
        record['compass'] = extra_fields

    return record


class _DatadogJsonAdapter(logging.LoggerAdapter):

    level_to_str = {
        0: 'NOTSET',
        10: 'DEBUG',
        20: 'INFO',
        30: 'WARNING',
        40: 'ERROR',
        50: 'CRITICAL',
    }

    def log(self, level, msg, *args, **kwargs):
        """
        Delegate a log call to the underlying logger, after adding
        contextual information from this adapter instance. Passes log level to
        process() as well.
        """
        if self.isEnabledFor(level):
            msg, kwargs = self.process(level, msg, kwargs)
            self.logger.log(level, msg, *args, **kwargs)

    def process(self, level, msg, kwargs):
        record = _format_datadog_log(self.level_to_str[level], msg,
            logger=self.logger.name,
            extra_fields=kwargs.pop('extra_fields', None),
            # We pop exc_info because we don't want the underlying logger to
            # handle it and print the exception again on multiple lines, since
            # we already add the stack trace to the record
            err=kwargs.pop('exc_info', None))

        return json.dumps(record, sort_keys=True), kwargs


class _LevelFilter(logging.Filter):
    """Filter for logs that fall in a given range of log levels

    Taken from: https://stackoverflow.com/questions/36337244/
    """

    def __init__(self, low, high):
        self._low = low
        self._high = high
        logging.Filter.__init__(self)

    def filter(self, record):
        if self._low <= record.levelno <= self._high:
            return True
        return False


def get_docker_dd_json_logger(name, level=logging.INFO):
    """Configure a logger for sending logs in JSON to Datadog from a Docker
    container.

    Datadog magically parses JSON logs. Docker containers usually log to
    stdout/stderr.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    f = logging.Formatter('%(message)s')

    # Log all WARNING and below logs to stdout
    h = logging.StreamHandler(sys.stdout)
    h.addFilter(_LevelFilter(0, logging.WARNING))
    h.setFormatter(f)
    logger.addHandler(h)

    # Log all ERROR and above logs to stderr
    eh = logging.StreamHandler(sys.stderr)
    eh.setLevel(logging.ERROR)
    eh.setFormatter(f)
    logger.addHandler(eh)

    return _DatadogJsonAdapter(logger, extra=None)
