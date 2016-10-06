from cnr.models.kv.channel_kv_base import ChannelKvBase
from cnr.models.kv.filesystem.models_index import ModelsIndexFilesystem


class Channel(ChannelKvBase):
    index_class = ModelsIndexFilesystem
