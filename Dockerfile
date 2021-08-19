FROM python:3.9.6-alpine3.14

WORKDIR /usr/src/app

COPY * ./
RUN mkdir data && pip install --no-cache-dir -r requirements.txt

#CMD python
CMD python docker_updater.py