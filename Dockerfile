FROM python:3-alpine

WORKDIR /app

COPY setup.py setup.py
# We use develop instead of install so that the source code that we copy in
# after installing the dependencies is discoverable by the package
RUN python setup.py develop

COPY app.py app.py
COPY toy/ toy/
COPY test/ test/

CMD flask run -h 0.0.0.0 -p 80
