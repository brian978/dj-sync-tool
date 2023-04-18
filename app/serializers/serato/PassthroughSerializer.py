import struct

from app.models.serato.PassthroughModel import PassthroughModel


class PassthroughSerializer(object):
    MODEL = PassthroughModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        info_size = struct.calcsize(model.FMT)
        info = struct.unpack(model.FMT, data[:info_size])
        entry_data = []

        for field, value in zip(model.FIELDS, info):
            entry_data.append(value)

        return model(*entry_data)
