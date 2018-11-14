# ------------------------------------------------------------------------------
# Opentracer API

# from ddtrace.opentracer import Tracer, set_global_tracer
#
# from os import environ as env
#
#
# def init_opentracer():
#     config = {
#         'agent_hostname': env.get('DATADOG_AGENT_HOST') or
#             env.get('DATADOG_TRACE_AGENT_HOSTNAME') or 'localhost',
#         'global_tags': {
#             'kube_namespace': env.get('KUBE_NAMESPACE', 'local'),
#             'kube_deployment': env.get('KUBE_DEPLOYMENT', 'local'),
#             'pod_name': env.get('KUBE_POD_NAME', 'local'),
#             'docker_image': env.get('DOCKER_IMAGE', 'local'),
#         },
#     }
#
#     service_name = env.get('KUBE_DEPLOYMENT', 'local')
#     tracer = Tracer(service_name, config=config)
#     set_global_tracer(tracer)
#     return tracer
#
#
# init_opentracer()

# ------------------------------------------------------------------------------
# Datadog tracer API

from ddtrace import tracer, config, patch_all

import logging
from os import environ as env

def init_tracer(service_name='local', distributed_tracing=False, debug=False):
    '''Initialize Datadog APM tracer client. This has to be called before any
    autoinstrumented modules are imported.

    Supports both configuration via function params or via environment
    variables (env vars override params).

    Args:
        service_name (str): name of the service that you are tracing
            Overridden by KUBE_DEPLOYMENT
        distributed_tracing (bool): enable distributed tracing
            Overridden by DATADOG_DISTRIBUTED_TRACING
        debug (bool): enable tracer debug logging
            Overridden by DATADOG_TRACE_DEBUG
    Returns:
        global datadog tracer instance
    '''
    config.flask.service_name = env.get('KUBE_DEPLOYMENT', service_name)
    tracer.set_tags({
        'kube_namespace': env.get('KUBE_NAMESPACE', 'local'),
        'kube_deployment': env.get('KUBE_DEPLOYMENT', service_name),
        'pod_name': env.get('KUBE_POD_NAME', 'local'),
        'docker_image': env.get('DOCKER_IMAGE', 'local'),
    })

    # Enable distributed tracing
    if env.get('DATADOG_DISTRIBUTED_TRACING', 'false') == 'true' or \
        distributed_tracing:
        config.flask['distributed_tracing_enabled'] = True
        config.requests['distributed_tracing'] = True
        tracer.configure(priority_sampling=True)

    # Enable debug logging via the same env var that ddtrace-run reads
    if env.get('DATADOG_TRACE_DEBUG', 'false').lower() == 'true' or debug:
        tracer.debug_logging = True
        logging.basicConfig(level=logging.DEBUG)

    # Init tracer, manually enable autoinstrumenting requests
    patch_all(requests=True)

    return tracer

init_tracer(service_name='toy-flask', distributed_tracing=True)

# ------------------------------------------------------------------------------
# App code

import requests

from flask import Flask

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    r = requests.get('https://raw.githubusercontent.com/DataDog/dd-trace-py/'
        'master/ddtrace/opentracer/tags.py')
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    return ("Hello World!\nPath: {}\n\nSome random python code: \n{}"
        .format(path, r.text))


if __name__ == '__main__':
    app.run()
