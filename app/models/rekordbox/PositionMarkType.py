import enum


class PositionMarkType(enum.IntEnum):
    CUE = 0
    LOOP = 4
    MEMORY = 99

    @classmethod
    def parse(cls, value):
        match value:
            case 0:
                return cls.CUE

            case 4:
                return cls.LOOP

            case 99:
                return cls.MEMORY

            case _:
                raise ValueError(f"Undefined position mark type {value}")
