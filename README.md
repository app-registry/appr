[![Coverage Status](https://coveralls.io/repos/github/cn-app-registry/cnr-server/badge.svg)](https://coveralls.io/github/cn-app-registry/cnr-server)

# cnr-server
## Install
1. git clone https://github.com/cn-app-registry/cnr-server.git && cd cnr-server
2. pip install -e . && pip install gunicorn
3. Run the cnr-server on port 5000 `gunicorn cnr.api.wsgi:app -b :5000`
   or "./run-server"

## storage

### Filesystem (default)
By default package are stored in `/tmp/cnr`
```
STORAGE=filesystem ./run-server.sh
```

### Etcd
```
STORAGE=redis ./run-server.sh
```

### Redis
```
STORAGE=redis ./run-server.sh
```
