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

        self.beatgrid = []

        # Data extracted from Rekordbox
        self.hot_cues = []
        self.cue_loops = []

        # Markers are the actual extracted data from Serato tags
        self.markers = {}

    def add_beatgrid_marker(self, tempo: Tempo):
        self.beatgrid.append(tempo)

    def add_hot_cue(self, hot_cue: HotCue):
        at_index = hot_cue.index
        if hot_cue.type == HotCueType.LOOP:
            self.cue_loops.insert(at_index, hot_cue)
        else:
            self.hot_cues.insert(hot_cue.index, hot_cue)

    def append_markers(self, source_name: str, tags: list):
        self.markers[source_name] = tags

    def get_markers(self, source_name: str):
        return self.markers[source_name]
