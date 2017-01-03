Submission is a [Flask](http://flask.pocoo.org/) application to manage submissions for the [2016 bird audio detection challenge](http://machine-listening.eecs.qmul.ac.uk/bird-audio-detection-challenge/). 
It is wrapped in a Docker container with an nginx and uwsgi servers, managed by supervisord. The Docker part is largely inspired by (https://github.com/tiangolo/uwsgi-nginx-flask-docker).

# INSTALLATION
 
### 1 - Clone the repository
```
$ git clone ...
$ cd /path/to/submission
```
 
### 2 - Create the db backup volume to be mounted
`$ mkdir db_backup`

### 3 - Run [postgres container](https://hub.docker.com/_/postgres/) and mount database to host volume
```
$ docker run \
    --name submission_db \
    -v $(pwd)/db_backup:/var/lib/postgresql/data/pgdata \
    -e POSTGRES_USER=myuser \
    -e POSTGRES_PASSWORD=mypassword \
    -e POSTGRES_DB=submission_db \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -d postgres
```
 
### 4 - Build flask app
`$ docker build -t submission .`
 
### 5 - Run flask app and link to database container
`$ docker run --name submission --link submission_db:submission_db -p 5455:80 -v $(pwd)/app:/app -d submission`
 
### 6 - Initialize db and migrate (https://flask-migrate.readthedocs.io/en/latest/)
```
$ docker exec submission python /app/manage.py db init
$ docker exec submission python /app/manage.py db migrate
$ docker exec submission python /app/manage.py db upgrade
```
 
### 7 - Enjoy
Now the app is available at http://example.com:5455

### 8 - More stuff in case you want to modify the app

#### Logs
The logs of the app (nginx, uwsgi, Flask errors...) can be seen with
`docker logs <submissioncontainerid>`

where `<submissioncontainerid>` can be seen with

`docker ps`

#### Migrations
If you change the models, make sure to run the migrations, which are managed by [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/).

#### Supervisord
After any change, restart uwsgi:

`docker exec submission supervisorctl restart uwsgi`

 
# ADMINISTRATION
 
 The administration panel can be found at http://example.com:5455/admin.
 
### 1 - Login using the default admin user
email: admin@example.com
password: changeme
 
### 2 - VERY IMPORTANT: change the admin password

This can be done by editing the admin user data in http://example.com:5455/admin/user/.
 
### 3 - Create a competition
Competitions can be created from http://example.com:5455/admin/competition/. 
For each competition a ground truth must be uploaded, in the format: 
 
`<id>,<detection probability> `
 
where `<id>` is the identifier of the test instance and `<detection probability>` is self-explanatory (usually 0 or 1 for the ground truth). 
 
Example: 
 
```
$ cat groundtruth.csv
0,0 
1,0 
2,1 
3,0 
...
```

### 4 - Scores
User scores can be seen graphically at http://example.com:5455/scores.

Submissions ca be seen in the administration panel at http://example.com:5455/admin/submission/.

The submission files are stored in the path specified in config.py.
