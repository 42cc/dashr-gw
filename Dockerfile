FROM python:2.7
ENV PYTHONUNBUFFERED 1

# update the repository sources list
# and install dependencies
RUN apt-get update \
    && apt-get install -y nodejs npm curl yui-compressor node-less \
    && apt-get -y autoclean

ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD . /app
WORKDIR /app

EXPOSE 8000
ENV PORT 8000

CMD ["uwsgi", "/app/gateway/wsgi/uwsgi.ini"]
