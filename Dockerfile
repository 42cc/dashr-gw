FROM python:2.7
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app/

COPY requirements.txt package.json /usr/src/app/

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - \
    && apt install -y nodejs python-keyczar \
    && npm install -g less webpack \
    && pip install --no-cache-dir -r requirements.txt uwsgi \
    && npm install

COPY . /usr/src/app/

RUN (keyczart create --location=fieldkeys --purpose=crypt \
    && keyczart addkey --location=fieldkeys --status=primary --size=256) || true

RUN webpack -p && make collectstatic
