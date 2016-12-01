# cnr-server

[![build status](https://gitlab.com/cn-app-registry/cnr-server/badges/master/build.svg)](https://gitlab.com/cn-app-registry/cnr-server/commits/master)
[![Coverage Status](https://coveralls.io/repos/github/cn-app-registry/cnr-server/badge.svg)](https://coveralls.io/github/cn-app-registry/cnr-server)
[![Swagger API Reference](https://img.shields.io/badge/swagger-docs-blue.svg)](Documentation/cnr-api-swagger.yaml)

CNR implements a registry for storing Kubernetes application manifests that attempts to reuse as much knowledge from the rest of the Linux container ecosystem as possible.

Differentiating features include:

- A protocol and data model that can more easily be implemented by pre-existing container registries
  - This includes a common API for uploading, downloading, and searching for applications
- The reuse and integration with many elements from [OCI](https://www.opencontainers.org)
  - Content addressable manifest scheme for security, signing, and non-trusted mirroring
  - Reuse of common data structures such as Descriptors
  - Unification of Manifest Lists as the means of content negoitation for both Images and Applications

## Getting started

1. git clone https://github.com/cn-app-registry/cnr-server.git && cd cnr-server
2. pip install -e . && pip install gunicorn
3. Run the cnr-server on port 5000 `gunicorn cnr.api.wsgi:app -b :5000`
   or "./run-server"
4. See the [curl-based examples](Documentation/test.sh)

## Architecture at a glance

There are two top-level objects:

- Package: metadata describing an application
- Blob: a gzipped tarball of the package encoded in base64

Packages are primarily indexed by 3 notable fields:

- package-name: it follows container-image format: `namespace/name`.
- release: it's the version of the package, immutable it can be viewed as an alias to a digest
- mediaType: the format of the package formats (eg: docker-compose, dab, helm, kpm)

Data storage is specified by the `STORAGE` environment variable. The following are supported:

- `filesystem` (default)
- [`etcd`](https://github.com/coreos/etcd)
- [`redis`](https://github.com/antirez/redis)

## Demo using using [Helm](https://github.com/kubernetes/helm) charts

### Publish a chart

Create and encode the chart tarball

```
~/charts/elasticsearch $
tar czvf ../elastichart.tar.gz  Chart.yaml manifests README.md
cat ../elastichart.tar.gz | base64 -w 0
H4sIAGBoF1gAA+2XTY/aMBCGc86vGKlngk02iRpVq1aUQw+VKlr1bowhVp0P2QZp/33tZFkCy0dVAburnUdCBs/EMyR5XyfjgmkbPbBSBVeDONL0zo80S0h/bInTLKAxIUmaxkmSBoTSu3QUALleS1tWxjINELDKxvRE3rn4G6VipchBKGas5EYwzYuwqP1cYW1j8uFwKW2xmkW8LoePacPd9LXQRtZVDiQaRSScC8O1bGw7NelnwlQYu1gp+Nn9nFRLWYmwZLKy7uOWyUOAAXxjFYzrxUI8wCfJ2y+f50Ia38O9W98lqzb1VyENjP0dDI2u19KVBgYzZiTfq/w06LXkIgpf+rS/GkpWyYW7LGZ4vRpe41mWHNW/Y1//yYgEkFyvpS3vXP/b678j6oFZ84vtCmf9P4n3rn9KKEH/vwWskb83/r2m4R9ZzXPnz61NhqWz2jmzzHvtoY0CQLGZ6LwYNhasn2cBFEJLy5Z+WxGqDE0juD+oqbV9NP1ufa6kqGy3nIvl8HFESC/eCKH70biNGqEEt7U+3cdLn+pXyTH968vJ/6z+M0r39J+kNEP934KD+p+KRknO/CPcuK6srpVysru6G+iurMmB/rOoAawoG8Ws6PL6TXoON+rpN3uu4U2HHl73n1Y9gxNVAGTZ/tOdYD6KaES3pTc2uFnvqcaPvgkei3oT/F93m06+fP0+icr5Re+qXc7pn9L9/Z+6SdT/Lfiw+6IUhvhOhSAIgiAIgiAIgiAIgiAIgiBvnr97lKMIACgAAA==
```

POST the chart to CNR

```
curl -XPOST http://localhost:5000/api/v1/packages/myname/elasticsearch -d '
{
  "blob": "H4sIAP3mAFgAA....",
  "release": "2.2.1",
  "media_type": "helm"
}'
```

### Pull the chart

Find the digest from the package-name/release/media-type

```
curl -XGET http://localhost:5000/api/v1/packages/myname/elasticsearch/2.2.1/helm
{
  "channels": [],
  "content": {
    "digest": "72ed15c9a65961ecd034cca098ec18eb99002cd402824aae8a674a8ae41bd0ef",
    "mediaType": "application/vnd.cnr.package.helm.v1.tar+gzip",
    "size": 583,
    "urls": []
  },
  "created_at": "2016-11-16T17:13:07.806579",
  "mediaType": "application/vnd.cnr.package-manifest.helm.v1.json",
  "package": "myname/elasticsearch",
  "release": "2.2.1"
}

```

Fetch the blob

```
curl -XGET \
http://localhost:5000/api/v1/packages/myname/elasticsearch/blobs/sha256/72ed15c9a65961ecd034cca098ec18eb99002cd402824aae8a674a8ae41bd0ef \
-o elasticsearch-chart.tar.gz
```
