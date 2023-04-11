from app.models.HotCueType import HotCueType
from app.models.rekordbox.PositionMarkType import PositionMarkType


class TypeMap:
    @classmethod
    def to_rb(cls, cue_type: HotCueType):
        match cue_type:
            case HotCueType.CUE:
                return PositionMarkType.CUE

            case HotCueType.LOOP:
                return PositionMarkType.LOOP

            case _:
                raise TypeError("Unsupported CUE type")

    @classmethod
    def from_rb(cls, cue_type: PositionMarkType):
        match cue_type:
            case PositionMarkType.CUE:
                return HotCueType.CUE

            case PositionMarkType.LOOP:
                return HotCueType.LOOP

            case _:
                return HotCueType.INVALID
