# Toy Flask

This is a barebones flask setup. Includes:
1. A simple flask server that returns "Hello World!" at the base route
1. Alpine-based Dockerfile
1. Docker-compose file to run 3 replicas behind an nginx loadbalancer

Also includes Datadog APM and Logs integration, properly correlating logs with
traces by injecting trace_ids into logs.

----------

## Requirements

1. Docker
1. Docker Compose (preinstalled w/ Docker for Mac)

## Starting the application

(You'll also need a suitably configured Datadog agent to verify the
tracing/logging behavior)

```bash
  docker-compose build
  docker-compose run hello1 py.test
  docker-compose up
```
