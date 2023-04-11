import struct

from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class BpmLockSerializer(EntrySerializer):
    MODEL = BpmLockModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        return model(*struct.unpack(model.FMT, data))
