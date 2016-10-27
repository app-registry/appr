curl -XPOST http://localhost:5000/api/v1/packages/foo/bar -d '{"blob": "H4sIAP3mAFgAA+3OMQqEMBCF4ak9RU4gGaPxPClcVogKGou9/SpYrI2yhYjwf82DeVO8LvTtq5lS/gldlGvYhfflmlpX9jc3XtStV++KSsVqobUTYy/aszNPKYzGSOiT04O/s/6h3k2MQ3b3CgAAAAAAAAAAAAAAAADAv77X4+BWACgAAA==", "release": "1.0.1", "media_type": "kpm"}'

curl -XPOST http://localhost:5000/api/v1/packages/foo/bar -d '{"blob": "H4sIANXqAFgAA+3OMQqDQBCF4alzij2BzLBxcgBPsoVgsUlA1yK3j4KFlWIhIvxf82DeFK/pUl+G6pfeWc6iE/fnnPaqdZ0LF4vz1euoUdTMzSToaYtWxqGkPgRJnxJt42+vv6muzfn7uHoFAAAAAAAAAAAAAAAAAOCoPyJ7ugAAKAAA", "release": "1.0.1", "media_type": "helm"}'

curl -XPOST http://localhost:5000/api/v1/packages/toto/titi -d '{"blob": "H4sIANXqAFgAA+3OMQqDQBCF4alzij2BzLBxcgBPsoVgsUlA1yK3j4KFlWIhIvxf82DeFK/pUl+G6pfeWc6iE/fnnPaqdZ0LF4vz1euoUdTMzSToaYtWxqGkPgRJnxJt42+vv6muzfn7uHoFAAAAAAAAAAAAAAAAAOCoPyJ7ugAAKAAA", "release": "4.2.1", "media_type": "helm"}'

curl -XPOST http://localhost:5000/api/v1/packages/toto/titi -d '{"blob": "H4sIANXqAFgAA+3OMQqDQBCF4alzij2BzLBxcgBPsoVgsUlA1yK3j4KFlWIhIvxf82DeFK/pUl+G6pfeWc6iE/fnnPaqdZ0LF4vz1euoUdTMzSToaYtWxqGkPgRJnxJt42+vv6muzfn7uHoFAAAAAAAAAAAAAAAAAOCoPyJ7ugAAKAAA", "release": "3.2.1", "media_type": "helm"}'


curl -XGET http://localhost:5000/api/v1/packages

curl -XGET "http://localhost:5000/api/v1/packages/foo/bar/1.0.1/helm"

curl -XGET "http://localhost:5000/api/v1/packages/foo/bar/blobs/sha256/92ba810abfe250d43cea35bad65906a7e199cd50b6cfeead6c66d31844223885" -o foo_bar-92ba810a.tar.gz

curl -XGET "http://localhost:5000/api/v1/packages/foo/bar/1.0.1/kpm"

curl -XGET "http://localhost:5000/api/v1/packages/foo/bar/blobs/sha256/7da12a2f437eb6a327e0fc922c3d50c4a8259b8054ac358711d0de8a4fc178c0" -o foo_bar-7da12a2.tar.gz

curl -XDELETE "http://localhost:5000/api/v1/packages/foo/bar/1.0.1/helm"
