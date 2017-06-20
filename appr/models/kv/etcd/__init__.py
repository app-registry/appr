import os
import etcd


class EtcdClient(etcd.client.Client):
    pass


ETCD_HOST = os.getenv("ETCD_HOST", "localhost")
etcd_client = EtcdClient(host=ETCD_HOST, port=2379)
