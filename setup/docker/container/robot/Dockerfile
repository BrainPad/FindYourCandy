FROM brainpad/fyc-base:latest

WORKDIR /opt/FindYourCandy
ARG container_dir="setup/docker/container/robot"

# Python libraries
COPY robot-arm/requirements.txt robot-arm/
RUN set -ex \
  && pip install -r robot-arm/requirements.txt \
  && rm -rf ~/.cache/pip

# Nginx
COPY ${container_dir}/nginx-robot.conf /etc/nginx/conf.d/

# uWSGI
RUN set -ex && mkdir /etc/uwsgi /run/uwsgi
COPY ${container_dir}/uwsgi-robot.ini /etc/uwsgi/

# Supervisor
COPY ${container_dir}/supervisord-robot.conf /etc/supervisor/conf.d/

# Application
COPY robot-arm robot-arm
COPY setup/script/robot_tune.py setup/script/
RUN set -ex && ln -sf /proc/$$/fd/1 robot-arm/logs/app.log

EXPOSE 80
CMD ["/usr/bin/supervisord"]
