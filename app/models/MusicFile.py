import logging
import os

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.Offset import Offset
from app.models.Tempo import Tempo
from app.utils import finder
from app.utils.prompt import CliColor, color_msg


class MusicFile:
    def __init__(self, path: str):
        self.location = os.path.abspath(path.replace('file://localhost', ''))
        self.trackID = ''
        self.averageBpm: float = 0.0
        self.dateAdded = ''
        self.playCount = ''
        self.tonality = ''
        self.totalTime: float = 0.0

        self.beatgrid: list[Tempo] = []

        # Data extracted from Rekordbox
        self.hot_cues: list[HotCue] = list()
        self.cue_loops: list[HotCue] = list()

        # Markers are the actual extracted data from Serato tags
        self.__tag_data = {}

    def is_file(self) -> bool:
        return os.path.isfile(self.location)

    def filename(self):
        return os.path.basename(self.location)

    @staticmethod
    def _logger() -> logging.Logger:
        return logging.getLogger(__name__)

    def add_beatgrid_marker(self, tempo: Tempo):
        self.beatgrid.append(tempo)

    def add_hot_cue(self, hot_cue: HotCue):
        at_index = hot_cue.index
        if hot_cue.type == HotCueType.LOOP:
            self.cue_loops.insert(at_index, hot_cue)
        else:
            self.hot_cues.insert(hot_cue.index, hot_cue)

    def add_tag_data(self, source_name: str, tags: list):
        self.__tag_data[source_name] = tags

    def get_tag_data(self, source_name: str):
        return self.__tag_data[source_name]

    def apply_beatgrid_offsets(self, offsets: list[Offset]):
        try:
            for hot_cue in self.hot_cues:
                hot_cue.offset = finder.closest_offset(hot_cue.start, offsets)
                hot_cue.apply_offset()

            for loop in self.cue_loops:
                loop.offset = finder.closest_offset(loop.start, offsets)
                loop.apply_offset()
        except ValueError as e:
            self._logger().error(color_msg(CliColor.FAIL, f'Error: {e} | Track: {self.filename()}'))
