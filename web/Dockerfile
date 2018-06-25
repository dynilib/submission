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

# Install conda
RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

ENV PATH /opt/conda/bin:$PATH

# Create environment and install packages
COPY env.yml /tmp/
RUN conda env create -f /tmp/env.yml
ENV PATH /opt/conda/envs/submission/bin:$PATH

# Add app
ENV PYTHONPATH /myapp:/opt/conda/envs/submission/lib/python3.6/site-packages:/$PYTHONPATH
ENV FLASK_APP submission
ENV UWSGI_INI /myapp/uwsgi.ini
WORKDIR /myapp


CMD ["/usr/bin/supervisord"]

