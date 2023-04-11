import struct

from app.models.serato.EntryType import EntryType
from app.models.serato.EntryModel import EntryModel
from app.utils.serato.encoder import decode


class EntrySerializer(object):
    MODEL = EntryModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        info_size = struct.calcsize(model.FMT)
        info = struct.unpack(model.FMT, data[:info_size])
        entry_data = []

        start_position_set = None
        end_position_set = None
        for field, value in zip(model.FIELDS, info):
            if field == 'start_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                start_position_set = value
            elif field == 'end_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                end_position_set = value
            elif field == 'start_position':
                assert start_position_set is not None
                if start_position_set:
                    value = struct.unpack('>I', decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'end_position':
                assert end_position_set is not None
                if end_position_set:
                    value = struct.unpack('>I', decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'color':
                value = decode(value)
            elif field == 'type':
                value = EntryType(value)
            entry_data.append(value)

        return model(*entry_data)