import struct

from app.models.serato.v2.ColorModel import ColorModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class ColorSerializer(EntrySerializer):
    MODEL = ColorModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        return model(*struct.unpack(model.FMT, data))
