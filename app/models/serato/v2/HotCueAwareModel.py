from abc import abstractmethod, ABC

from app.models.HotCue import HotCue


class HotCueAwareModel(ABC):
    @classmethod
    @abstractmethod
    def from_hot_cue(cls, hot_cue: HotCue):
        pass
