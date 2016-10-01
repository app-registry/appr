# cnr-server
## Install
1. Install etcd from a [recent release](https://github.com/coreos/etcd) and simply run `etcd` with no arguments.
2. pip install cnr-server && pip install gunicorn
3. Run the cnr-server on port 5000 `gunicorn cnr.api.wsgi:app -b :5000`

## Storage
The server stores the contents, multiple datastore can be used and models customized.
Base models are:
 - Package:
    - blob
    - digest
    - release
    - name
    - created_at
 - Channel
    - name
    - releases
    - current

The package is the content that can be addressed via its unique name in the format: "namespace/content-name" or its digest.
Channel allow to organize and tag packages, e.g: channel 'stable'.

### Etcd
The structure in etcd is the following:

``` shell
/cnr/packages/{namespace}/{package_name}/releases/{release} -> package-data {blob/digest/created_at...}
/cnr/packages/{namespace}/{package_name}/channels/{channel_name} -> link/path to a release (/cnr/packages/{namespace}/{package_name}/releases/{release})
/cnr/packages/{namespace}/{package_name}/digests/{digest} -> link/path to a release (/cnr/packages/{namespace}/{package_name}/releases/{release})
```

Example:

#### Search
And index is created on package add / delete and stored in:
/cnr/search/index

#### Track delated releases

/cnr/packages/{namespace}/{package_name}/deleted/{release} -> delete-info {digest/deleted_at}
