FROM tiangolo/uwsgi-nginx:python3.6

# By default, allow unlimited file sizes, modify it to limit the file sizes
# To have a maximum of 1 MB (Nginx's default) change the line to:
# ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_MAX_UPLOAD 0

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path of the static files
ENV STATIC_PATH /myapp/static

# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Add demo app

ENV PYTHONPATH /myapp
ENV FLASK_APP submission
ENV UWSGI_INI /myapp/uwsgi.ini
WORKDIR /myapp

#RUN pip install flask
COPY submission/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

CMD ["/usr/bin/supervisord"]

