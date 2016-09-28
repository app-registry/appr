import etcd
import re

ETCD_PREFIX = "cnr/packages/"


class EtcdClient(etcd.client.Client):
    pass


etcd_client = EtcdClient(port=2379)


def etcd_listkeys(key, path):
    result = []
    for child in key.children:
        m = re.match("^/%s/(.+)$" % path, child.key)
        if m is None:
            continue
        result.append(m.group(1))
    return result
