import etcd


class EtcdClient(etcd.client.Client):
    pass


etcd_client = EtcdClient(port=2379)
