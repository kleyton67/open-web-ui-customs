FROM python:3.11.12-alpine3.21

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    apk add wget --no-cache && \
    apk add --no-cache firefox && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz &&\
    tar -xvzf geckodriver-v0.36.0-linux64.tar.gz &&\
    chmod +x /usr/src/app/geckodriver && \
    apk add --no-cache supervisor

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/supervisord.conf /etc/supervisord.conf

EXPOSE 8888 8889

ENTRYPOINT ["/entrypoint.sh"]
