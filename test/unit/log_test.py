import json
import logging

from toy.log import _format_datadog_log, _DatadogJsonAdapter
from logcapture import LogCapture


def test_format_datadog_log_has_dd_special_attrs():
    """This test is semi-tautological. It just verifies that this function
    generates a dict with the required Datadog attributes"""
    record = _format_datadog_log('level', 'message')

    for attr in ['time', 'status', 'message', 'logger', 'dd']:
        assert attr in record

    for attr in ['name', 'thread_name']:
        assert attr in record['logger']

    for attr in ['trace_id', 'span_id']:
        assert attr in record['dd']


def test_format_datadog_log_has_dd_err_attrs():
    record = _format_datadog_log('level', 'message',
        err=Exception('exception'))

    assert 'error' in record
    for attr in ['kind', 'message', 'stack']:
        assert attr in record['error']


def test_format_datadog_log_has_custom_attrs():
    record = _format_datadog_log('level', 'message',
        extra_fields=dict(param='val'))

    assert 'compass' in record
    assert 'val' == record['compass']['param']


class TestDatadogJsonAdapter(object):

    @classmethod
    def config_logger(cls, logger):
        return logger

    def test_log(self):
        logger = logging.getLogger(
            '{}.{}'.format(self.__class__.__name__, 'test_log'))
        with LogCapture(logger, level=logging.INFO) as log_cap:
            adapter = _DatadogJsonAdapter(logger, extra=None)
            adapter.info('log message')

        record = json.loads(log_cap.last_logs)
        assert record['status'] == 'INFO'
        assert record['message'] == 'log message'


