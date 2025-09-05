# Stage 1: Base image with system dependencies and configurations
# Stage 1: Base image with system dependencies and configurations
FROM jhpyle/docassemble-os AS base
SHELL ["/bin/bash", "-c"]

RUN DEBIAN_FRONTEND=noninteractive TERM=xterm LC_CTYPE=C.UTF-8 LANG=C.UTF-8 \
    bash -c \
    "apt-get -y update && apt-get install -y inotify-tools && ln -s /var/mail/mail /var/mail/root"

# Copy configuration files and scripts that don't change often
COPY Docker/ /tmp/Docker/
RUN chmod +x /tmp/Docker/wait-for-postgres.sh
RUN DEBIAN_FRONTEND=noninteractive TERM=xterm LC_CTYPE=C.UTF-8 LANG=C.UTF-8 \
    bash -c \
    "cp /tmp/Docker/*.sh /usr/share/docassemble/webapp/ && \
    cp /tmp/Docker/VERSION /usr/share/docassemble/webapp/ && \
    cp /tmp/Docker/pip.conf /usr/share/docassemble/local3.12/ && \
    cp /tmp/Docker/config/* /usr/share/docassemble/config/ && \
    cp /tmp/Docker/cgi-bin/index.sh /usr/lib/cgi-bin/ && \
    cp /tmp/Docker/syslog-ng.conf /usr/share/docassemble/webapp/syslog-ng.conf && \
    cp /tmp/Docker/syslog-ng-docker.conf /usr/share/docassemble/webapp/syslog-ng-docker.conf && \
    cp /tmp/Docker/smart-multi-line.fsm /usr/share/syslog-ng/smart-multi-line.fsm && \
    cp /tmp/Docker/docassemble-syslog-ng.conf /usr/share/docassemble/webapp/docassemble-syslog-ng.conf && \
    cp /tmp/Docker/apache.logrotate /etc/logrotate.d/apache2 && \
    cp /tmp/Docker/nginx.logrotate /etc/logrotate.d/nginx && \
    cp /tmp/Docker/docassemble.logrotate /etc/logrotate.d/docassemble && \
    cp /tmp/Docker/cron/docassemble-cron-monthly.sh /etc/cron.monthly/docassemble && \
    cp /tmp/Docker/cron/docassemble-cron-weekly.sh /etc/cron.weekly/docassemble && \
    cp /tmp/Docker/cron/docassemble-cron-daily.sh /etc/cron.daily/docassemble && \
    cp /tmp/Docker/cron/docassemble-cron-hourly.sh /etc/cron.hourly/docassemble && \
    cp /tmp/Docker/cron/syslogng-cron-daily.sh /etc/cron.daily/logrotatepost && \
    cp /tmp/Docker/cron/donothing /usr/share/docassemble/cron/donothing && \
    cp /tmp/Docker/docassemble.conf /etc/apache2/conf-available/ && \
    cp /tmp/Docker/docassemble-behindlb.conf /etc/apache2/conf-available/ && \
    cp /tmp/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf && \
    cp /tmp/Docker/supervisor-yaml-watcher.conf /etc/supervisor/conf.d/supervisor-yaml-watcher.conf && \
    mkdir -p /usr/share/docassemble/scripts && \
    cp /tmp/Docker/watch-yaml-robust.sh /usr/share/docassemble/scripts/watch-yaml-changes.sh && \
    cp /tmp/Docker/start-yaml-watcher.sh /usr/share/docassemble/scripts/start-yaml-watcher.sh && \
    chmod +x /usr/share/docassemble/scripts/watch-yaml-changes.sh && \
    chmod +x /usr/share/docassemble/scripts/start-yaml-watcher.sh && \
    chown www-data:www-data /usr/share/docassemble/scripts/watch-yaml-changes.sh && \
    cp /tmp/Docker/ssl/* /usr/share/docassemble/certs/ && \
    cp -r /tmp/Docker/ssl /usr/share/docassemble/config/defaultcerts && \
    chmod og-rwx /usr/share/docassemble/certs/* && \
    chmod og-rwx /usr/share/docassemble/config/defaultcerts/* && \
    cp /tmp/Docker/rabbitmq.config /etc/rabbitmq/ && \
    cp /tmp/Docker/config/exim4-router /etc/exim4/conf.d/router/101_docassemble && \
    cp /tmp/Docker/config/exim4-filter /etc/exim4/docassemble-filter && \
    cp /tmp/Docker/config/exim4-main /etc/exim4/conf.d/main/01_docassemble && \
    cp /tmp/Docker/config/exim4-acl /etc/exim4/conf.d/acl/29_docassemble && \
    cp /tmp/Docker/config/exim4-update /etc/exim4/update-exim4.conf.conf && \
    cp /tmp/Docker/config/nascent.conf /usr/share/docassemble/config/nascent.conf && \
    cp /tmp/Docker/daunoconv /usr/bin/daunoconv && \
    chmod ogu+rx /usr/bin/daunoconv && \
    update-exim4.conf && \
    chmod 755 /etc/ssl/docassemble && \
    echo \"en_US.UTF-8 UTF-8\" >> /etc/locale.gen && \
    locale-gen && \
    update-locale && \
    rm -rf /tmp/Docker"

# Stage 2: Builder for Python dependencies
FROM base AS builder

WORKDIR /tmp/src

# Create Python virtual environment
RUN python3 -m venv --copies /usr/share/docassemble/local3.12 && \
    source /usr/share/docassemble/local3.12/bin/activate && \
    pip install --upgrade pip==25.1.1 wheel==0.45.1 mod_wsgi==5.0.2 && \
    pip install --break-system-packages unoconv && \
    cp /usr/share/docassemble/local3.12/bin/unoconv /usr/bin/unoconv

# Install third-party Python packages
COPY Docker/requirements.txt /tmp/src/requirements.txt
RUN source /usr/share/docassemble/local3.12/bin/activate && \
    pip install -r /tmp/src/requirements.txt

# Install docassemble packages
COPY docassemble_base/ /tmp/src/docassemble_base/
COPY docassemble_demo/ /tmp/src/docassemble_demo/
COPY docassemble_webapp/ /tmp/src/docassemble_webapp/
RUN source /usr/share/docassemble/local3.12/bin/activate && \
    pip install ./docassemble_base && \
    pip install ./docassemble_demo && \
    pip install ./docassemble_webapp

# Stage 3: Run tests
FROM builder AS test

WORKDIR /tmp/src
COPY tests/ /tmp/src/tests/

ENV SUPERVISORLOGLEVEL=info
ENV DASUPERVISORUSERNAME=user
ENV DASUPERVISORPASSWORD=password

RUN useradd -m -s /bin/bash testuser && chown -R testuser:testuser /tmp/src && chown -R testuser:testuser /usr/share/docassemble
USER testuser

RUN /usr/bin/supervisord -c /etc/supervisor/conf.d/docassemble.conf && \
    /tmp/Docker/wait-for-postgres.sh localhost bash -c "source /usr/share/docassemble/local3.12/bin/activate && python3 -m unittest discover tests" && \
    supervisorctl -c /etc/supervisor/conf.d/docassemble.conf shutdown

# Stage 4: Final image
FROM base AS final

# Copy Python environment from builder stage
COPY --from=builder /usr/share/docassemble/local3.12 /usr/share/docassemble/local3.12

# Copy application code
COPY . /usr/share/docassemble/webapp/
WORKDIR /usr/share/docassemble/webapp/

# Fix startup files location issues
# Copy the fix-startup script and run it during build
COPY Docker/fix-startup.sh /usr/share/docassemble/webapp/fix-startup.sh
RUN chmod +x /usr/share/docassemble/webapp/fix-startup.sh && \
    /usr/share/docassemble/webapp/fix-startup.sh && \
    # Also ensure these fixes are applied at build time
    if [ -f /usr/share/docassemble/webapp/docassemble_webapp/docassemble.wsgi ]; then \
        cp /usr/share/docassemble/webapp/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/docassemble.wsgi; \
    else \
        echo "from docassemble.webapp.run import application" > /usr/share/docassemble/webapp/docassemble.wsgi; \
    fi && \
    mkdir -p /var/www && \
    touch /var/www/.pypirc && \
    chown www-data:www-data /var/www /var/www/.pypirc /usr/share/docassemble/webapp/docassemble.wsgi && \
    chmod 600 /var/www/.pypirc && \
    chmod 644 /usr/share/docassemble/webapp/docassemble.wsgi

# Final setup
RUN chown -R www-data:www-data /usr/share/docassemble && \
    # Perform other final setup steps from the original Dockerfile
    sed -i -e 's/^\(daemonize\s*\)yes\s*$/\1no/g' -e 's/^bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf && \
    sed -i -e 's/#APACHE_ULIMIT_MAX_FILES/APACHE_ULIMIT_MAX_FILES/' -e 's/ulimit -n 65536/ulimit -n 8192/' /etc/apache2/envvars && \
    sed -i '/session    required     pam_loginuid.so/c\#session    required   pam_loginuid.so' /etc/pam.d/cron && \
    LANG=en_US.UTF-8 && \
    a2dismod ssl && a2enmod rewrite && a2enmod xsendfile && a2enmod proxy && a2enmod proxy_http && a2enmod proxy_wstunnel && a2enmod headers && a2enconf docassemble && \
    echo 'export TERM=xterm' >> /etc/bash.bashrc

USER www-data
RUN source /usr/share/docassemble/local3.12/bin/activate && \
    python /usr/share/docassemble/webapp/Docker/nltkdownload.py && \
    # Other USER www-data commands
    cd /var/www/nltk_data/corpora && unzip -o wordnet.zip && unzip -o omw-1.4.zip

USER root
EXPOSE 80 443 9001 514 25 465 8080 8081 8082 5432 6379 4369 5671 5672 25672
ENV \
CONTAINERROLE="all" \
LOCALE="en_US.UTF-8 UTF-8" \
TIMEZONE="America/New_York" \
SUPERVISORLOGLEVEL="info" \
EC2="" \
S3ENABLE="" \
S3BUCKET="" \
S3ACCESSKEY="" \
S3SECRETACCESSKEY="" \
S3REGION="" \
DAHOSTNAME="" \
USEHTTPS="" \
USELETSENCRYPT="" \
LETSENCRYPTEMAIL="" \
BEHINDHTTPSLOADBALANCER="" \
DBHOST="" \
LOGSERVER="" \
REDIS="" \
RABBITMQ="" \
DASUPERVISORUSERNAME="" \
DASUPERVISORPASSWORD=""

CMD ["/bin/bash", "-c", "/usr/share/docassemble/webapp/fix-startup.sh && /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf"]
