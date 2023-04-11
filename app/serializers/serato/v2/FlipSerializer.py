import struct

from app.models.serato.v2.FlipModel import FlipModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class FlipSerializer(EntrySerializer):
    MODEL = FlipModel

    @classmethod
    def deserialize(cls, data):
        model = cls.MODEL

        info1_size = struct.calcsize(model.FMT1)
        info1 = struct.unpack(model.FMT1, data[:info1_size])
        name, nullbyte, other = data[info1_size:].partition(b'\x00')
        assert nullbyte == b'\x00'

        info2_size = struct.calcsize(model.FMT2)
        loop, num_actions = struct.unpack(model.FMT2, other[:info2_size])
        action_data = other[info2_size:]
        actions = []
        for i in range(num_actions):
            type_id, size = struct.unpack(model.FMT2, action_data[:info2_size])
            action_data = action_data[info2_size:]
            if type_id == 0:
                payload = struct.unpack('>dd', action_data[:size])
                actions.append(("JUMP", *payload))
            elif type_id == 1:
                payload = struct.unpack('>ddd', action_data[:size])
                actions.append(("CENSOR", *payload))
            action_data = action_data[size:]
        assert action_data == b''

        return model(*info1, name.decode('utf-8'), loop, num_actions, actions)
