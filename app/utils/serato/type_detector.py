from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.models.serato.v2.ColorModel import ColorModel
from app.models.serato.v2.CueModel import CueModel
from app.models.serato.v2.FlipModel import FlipModel
from app.models.serato.v2.LoopModel import LoopModel
from app.models.serato.v2.UnknownModel import UnknownModel


def detect(name):
    entry_type = UnknownModel
    for entry_cls in (BpmLockModel, ColorModel, CueModel, LoopModel, FlipModel):
        if entry_cls.NAME == name:
            entry_type = entry_cls
            break

    return entry_type
