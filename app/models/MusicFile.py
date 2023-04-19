import os

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.Tempo import Tempo


class MusicFile:
    def __init__(self, path: str):
        self.location = os.path.abspath(path.replace('file://localhost', ''))
        self.trackID = ''
        self.averageBpm = ''
        self.dateAdded = ''
        self.playCount = ''
        self.tonality = ''

        self.offset = 0
        self.beatgrid = []

        # Data extracted from Rekordbox
        self.hot_cues: list[HotCue] = list()
        self.cue_loops: list[HotCue] = list()

        # Markers are the actual extracted data from Serato tags
        self.__tag_data = {}

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

    def apply_beatgrid_offset(self, offset: int):
        for hot_cue in self.cue_loops:
            hot_cue.apply_offset(offset)

        for loop in self.cue_loops:
            loop.apply_offset(offset)
