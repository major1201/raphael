Raphael
=======

An OpenLDAP management system

## How to run?

### Prerequisite

- Python >= 3.4
- prepare a MySQL database
- prepare an OpenLDAP server

### Clone the repositry

```bash
cd /opt
git clone https://github.com/major1201/raphael.git
cd /opt/raphael
```

### Make virtual environment

```bash
pyvenv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

### Import database

```bash
mysql -uroot -p < scripts/raphael.sql
```

### Configuration

```bash
mkdir /etc/raphael
# copy the example config file to /etc/raphael
cp config.yml /etc/raphael
```

make some changes, `vim /etc/raphael/config.yml`

```yml
system:                    # system related config
  project_name: raphael    # should NOT be changed

logging:                   # logging parameters
  stdout:                  # stdout logging
    enable: true           # enable stdout or not
    format:                # logging format; default: '[%(asctime)s %(levelname)s %(name)s] %(message)s'
    level:                 # logging level; default: 0; 0: NOTSET, 10: DEBUG, 20: INFO, 30: WARNING, 40: ERROR, 50: FATAL/CRITICAL
  file:                    # file logging
    enable: false          # enable log to file or not
    level:
    path:                  # file path
    rotating:              # log file rotating
      enable: true         # enable log file rotating or not
      when: MIDNIGHT
      backup_count: 60
  loggers:                 # other logger to overwrite
    - name: requests
      level: 100
    - name: werkzeug
      level: 100

dao:                       # db connection
  url: mysql+mysqldb://raphael:raphael@127.0.0.1/raphael?charset=utf8 # db connection url
  pool_size: 20            # db pool size; default: 20
  max_overflow: 0          # db max overflow; default: 0
  pool_recycle: 5          # db pool recycle; default: 5
  pool_timeout: 3600       # db pool timeout;

cache:                     # db cache
  memcached:               # memcached config
    enabled: false         # enable memcached or not
    server_list:           # memcached server list
      - 127.0.0.1:11211

web:                       # web config
  listen_addr: 0.0.0.0     # listen address
  port: 8000               # listen port
  debug: false             # debug or not
  threaded: true           # threaded or not
  cookie_secret: b5b0215e4ed24ced8a0a2d3779bd81f2 # cookie secret
```

### Run

Run source code

```bash
python3 wsgi.py
```

Run with uwsgi + Systemd + Nginx

```bash
# copy uwsgi config file
cp uwsgi.ini /etc/raphael/uwsgi.ini

# create raphael service
cp scripts/raphael.service /etc/systemd/system/raphael.service
systemctl daemon-reload

# copy nginx config
cp scripts/raphael.conf /etc/nginx/conf.d
# make sure raphael.conf be included by the main nginx config file
# reload nginx service
systemctl reload nginx.service

# start raphael service
systemctl start raphael.service
```

### Config OpenLDAP parameters

1. Open your web browser and type <http://127.0.0.1:8000> (for example, default username and password is admin/111)
2. Click config link on the left and follow the directions

### Config your server clients' LDAP to point to your OpenLDAP server

## How to make an RPM package

```bash
cd /opt/raphael
make && make rpm
```

## License

MIT
