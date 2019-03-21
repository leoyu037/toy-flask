"""Datadog APM tracer config, ready for kubernetes and distributed tracing"""
from os import environ as env

import ddtrace


def init_tracer(service_name):
    """Initialize and return Datadog APM tracer client.

    This has to be called before any autoinstrumented modules are imported.
    Supports both configuration via function params or via environment variables (env vars override
    params).

    :param service_name: The name of the service that you are tracing. Overridden by $KUBE_DEPLOYMENT
    :rtype: ddtrace.tracer.Tracer
    """
    ddtrace.tracer.configure(
        hostname=env.get('DATADOG_AGENT_HOST', 'localhost'),
        port=8126
    )

    ddtrace.tracer.set_tags({
        'kube_namespace': env.get('KUBE_NAMESPACE', 'local'),
        'kube_deployment': env.get('KUBE_DEPLOYMENT', service_name),
        'pod_name': env.get('KUBE_POD_NAME', 'local'),
        'docker_image': env.get('DOCKER_IMAGE', 'local'),
    })

    ddtrace.config.flask['service_name'] = env.get('KUBE_DEPLOYMENT',
        service_name)

    # Enable distributed tracing
    ddtrace.tracer.configure(priority_sampling=True)
    ddtrace.config.flask['distributed_tracing_enabled'] = True
    ddtrace.config.requests['distributed_tracing'] = True

    # Init tracer, manually enable autoinstrumenting requests module since it's
    # off be default: http://pypi.datadoghq.com/trace/docs/#supported-libraries
    ddtrace.patch_all(requests=True)

    return ddtrace.tracer
