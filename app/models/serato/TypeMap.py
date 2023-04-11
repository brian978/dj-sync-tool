from app.models.HotCueType import HotCueType
from app.models.serato.EntryType import EntryType


class TypeMap:
    @classmethod
    def to_serato(cls, cue_type: HotCueType):
        match cue_type:
            case HotCueType.CUE:
                return EntryType.CUE

            case HotCueType.LOOP:
                return EntryType.LOOP

            case _:
                return EntryType.INVALID

    @classmethod
    def from_serato(cls, cue_type: EntryType):
        match cue_type:
            case EntryType.CUE:
                return HotCueType.CUE

            case EntryType.LOOP:
                return HotCueType.LOOP

            case _:
                return HotCueType.INVALID
