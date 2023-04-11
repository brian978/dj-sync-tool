import struct

from app.models.serato.EntryModel import EntryModel


class FlipModel(EntryModel):
    NAME = 'FLIP'
    FMT1 = 'cB?'
    FMT2 = '>BI'
    FMT3 = '>BI16s'
    FIELDS = ('field1', 'index', 'enabled', 'name', 'loop', 'num_actions',
              'actions')

    @classmethod
    def load(cls, data):
        info1_size = struct.calcsize(cls.FMT1)
        info1 = struct.unpack(cls.FMT1, data[:info1_size])
        name, nullbyte, other = data[info1_size:].partition(b'\x00')
        assert nullbyte == b'\x00'

        info2_size = struct.calcsize(cls.FMT2)
        loop, num_actions = struct.unpack(cls.FMT2, other[:info2_size])
        action_data = other[info2_size:]
        actions = []
        for i in range(num_actions):
            type_id, size = struct.unpack(cls.FMT2, action_data[:info2_size])
            action_data = action_data[info2_size:]
            if type_id == 0:
                payload = struct.unpack('>dd', action_data[:size])
                actions.append(("JUMP", *payload))
            elif type_id == 1:
                payload = struct.unpack('>ddd', action_data[:size])
                actions.append(("CENSOR", *payload))
            action_data = action_data[size:]
        assert action_data == b''

        return cls(*info1, name.decode('utf-8'), loop, num_actions, actions)

    def dump(self):
        raise NotImplementedError('FLIP entry dumps are not implemented!')