from abc import ABC, abstractmethod

from app.models.serato.EntryType import EntryType
from app.utils.env import env


class LockableModel(ABC):
    @abstractmethod
    def is_start_position_set(self):
        pass

    def lock(self):
        setattr(self, 'is_locked', 1)

    def unlock(self):
        setattr(self, 'is_locked', 0)

    def locked(self):
        return getattr(self, 'is_locked') == 1

    def is_empty(self):
        return getattr(self, 'type') == EntryType.INVALID or not self.is_start_position_set()

    def is_writable(self) -> bool:
        if not env('OVERWRITE_CUES'):
            return self.is_empty()

        return not self.locked()
