FROM brainpad/fyc-opencv:latest

WORKDIR /opt/FindYourCandy
ARG container_dir="setup/docker/container/webapp"

# Python libraries
COPY webapp/requirements.txt webapp/
COPY webapp/requirements webapp/requirements
RUN set -ex \
  && pip install -r webapp/requirements.txt \
  && rm -rf ~/.cache/pip

# Nginx
COPY ${container_dir}/nginx-webapp.conf /etc/nginx/conf.d/

# uWSGI
RUN set -ex && mkdir /etc/uwsgi /run/uwsgi
COPY ${container_dir}/uwsgi-webapp.ini /etc/uwsgi/

# Supervisor
COPY ${container_dir}/supervisord-webapp.conf /etc/supervisor/conf.d/

# Application
COPY webapp webapp
COPY train train
COPY setup/script/camera_tune.py setup/script/
RUN set -ex && ln -sf /proc/$$/fd/1 webapp/logs/app.log

EXPOSE 80
CMD ["/usr/bin/supervisord"]
