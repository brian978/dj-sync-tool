import enum


class EntryType(enum.IntEnum):
    INVALID = 0
    CUE = 1
    LOOP = 3
    COLOR = 90
    BPM_LOCK = 91
    PASSTHROUGH = 100
