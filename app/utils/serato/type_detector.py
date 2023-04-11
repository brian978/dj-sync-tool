from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.models.serato.v2.ColorModel import ColorModel
from app.models.serato.v2.CueModel import CueModel
from app.models.serato.v2.FlipModel import FlipModel
from app.models.serato.v2.LoopModel import LoopModel
from app.serializers.serato.v2.BpmLockSerializer import BpmLockSerializer
from app.serializers.serato.v2.ColorSerializer import ColorSerializer
from app.serializers.serato.v2.CueSerializer import CueSerializer
from app.serializers.serato.v2.LoopSerializer import LoopSerializer
from app.serializers.serato.v2.UnknownEntrySerializer import UnknownEntrySerializer


def detect_type(name):
    match name:
        case BpmLockModel.NAME:
            return BpmLockSerializer
        case ColorModel.NAME:
            return ColorSerializer
        case CueModel.NAME:
            return CueSerializer
        case LoopModel.NAME:
            return LoopSerializer
        case FlipModel.NAME:
            return BpmLockSerializer
        case _:
            return UnknownEntrySerializer
