import enum


class PositionMarkType(enum.IntEnum):
    CUE = 0
    LOOP = 4

    @classmethod
    def parse(cls, value):
        match value:
            case 0:
                return cls.CUE

            case 4:
                return cls.LOOP

            case _:
                raise ValueError(f"Undefined position mark type {value}")
