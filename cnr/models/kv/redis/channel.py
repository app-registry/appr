from cnr.models.kv.channel_kv_base import ChannelKvBase
from cnr.models.kv.redis.models_index import ModelsIndexRedis


class Channel(ChannelKvBase):
    index_class = ModelsIndexRedis
