import struct

from app.models.serato.v2.LoopModel import LoopModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class LoopSerializer(EntrySerializer):
    MODEL = LoopModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        info_size = struct.calcsize(model.FMT)
        info = struct.unpack(model.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''

        return model(*info, name.decode('utf-8'))
