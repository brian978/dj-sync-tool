from app.models.serato.AbstractModel import AbstractModel
from app.models.serato.ColorMap import ColorMap
from app.models.serato.EntryType import EntryType
from app.models.serato.LockableModel import LockableModel


class EntryModel(AbstractModel, LockableModel):
    FIELDS: tuple = (
        'start_position_set',
        'start_position',
        'end_position_set',
        'end_position',
        'field5',
        'color',
        'type',
        'is_locked'
    )

    def set_hot_cue(self, position: int, color: str):
        if self.locked():
            return

        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position)
        setattr(self, 'type', EntryType.CUE)
        setattr(self, 'color', bytes.fromhex(ColorMap.to_serato(color)))

    def set_cue_loop(self, position_start: int, position_end: int):
        if self.locked():
            return

        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position_start)
        setattr(self, 'end_position_set', True)
        setattr(self, 'end_position', position_end)
        setattr(self, 'type', EntryType.LOOP)
        setattr(self, 'color', bytes.fromhex("27AAE1"))

    def is_start_position_set(self):
        return getattr(self, 'start_position_set') == True
