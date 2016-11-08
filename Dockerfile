FROM debian:8.5

# Install miniconda
RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.1.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

ENV PATH /opt/conda/bin:$PATH

##########################################
# Install flask and other Python modules #
##########################################

# Install conda packages (directly in root env, no need for more envs)
RUN conda install -y flask ipython psycopg2 numpy scikit-learn

# Install Python non-conda packages	
RUN pip install flask-sqlalchemy && \
	pip install flask-admin && \
	pip install flask-security && \
	pip install flask-migrate && \
	pip install flask-script

# Install uWSGI
RUN apt-get update && apt-get install -y build-essential python-dev && \
        pip install uwsgi

# Standard set up Nginx
ENV NGINX_VERSION 1.9.11-1~jessie

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
        && echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
        && apt-get update \
        && apt-get install -y ca-certificates nginx=${NGINX_VERSION} gettext-base

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
        && ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443
# Finished setting up Nginx

# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Remove default configuration from Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
#COPY uwsgi.ini /etc/uwsgi/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor

# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
#COPY ./app /app
WORKDIR /app
CMD ["/usr/bin/supervisord"]
