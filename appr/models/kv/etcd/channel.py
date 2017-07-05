from __future__ import absolute_import, division, print_function

from appr.models.kv.channel_kv_base import ChannelKvBase
from appr.models.kv.etcd.models_index import ModelsIndexEtcd


class Channel(ChannelKvBase):
    index_class = ModelsIndexEtcd
