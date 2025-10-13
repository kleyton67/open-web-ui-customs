FROM python:3.11.12-alpine3.21

COPY . /usr/src/app

# Install dependencies
RUN apk add --no-cache \
    supervisor &&  \
    /usr/local/bin/python3.11 -m pip install -r  /usr/src/app/requirements.txt && \
    apk add --no-cache firefox && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz &&\
    tar -xvzf geckodriver-v0.36.0-linux64.tar.gz &&\
    chmod +x geckodriver && \
    apk add --no-cache supervisor && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /etc/supervisord.d/programs && \
    mkdir -p /var/logs

# Copy individual program config files
COPY docker/fastapi.conf /etc/supervisord.d/programs/fastapi.conf
COPY docker/fastmcp.conf /etc/supervisord.d/programs/fastmcp.conf

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/supervisord.conf /etc/supervisord.d/supervisord.conf

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
