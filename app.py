from toy.apm import init_tracer
init_tracer('toy-flask')

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from toy.log import get_docker_dd_json_logger

app = Flask(__name__)
logger = get_docker_dd_json_logger(__name__)


@app.errorhandler(Exception)
def handle_error(e):
    # Taken straight from https://stackoverflow.com/questions/29332056/global-error-handler-for-any-exception
    code = 500
    if isinstance(e, HTTPException):
        code = e.code

    logger.error('Uncaught exception', extra_fields={'status_code': code},
        exc_info=e)
    return jsonify(error=str(e)), code


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    logger.info('Path: {}'.format(path))

    if path == 'err':
        # Example of logging a caught exception
        try:
            raise Exception('I\'m an exception!')
        except Exception as e:
            logger.error('This is an exception', exc_info=e)

        # Example of logging an uncaught exception
        raise Exception('I\'m an uncaught exception!')

    return 'Hello World!\nPath: {}'.format(path)
