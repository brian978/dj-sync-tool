import enum


class HotCueType(enum.IntEnum):
    CUE = 0
    LOOP = 1
    INVALID = 99
    PASSTHROUGH = 100
