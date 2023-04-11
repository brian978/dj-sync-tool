import os

from app.models.HotCue import HotCue


class MusicFile:
    def __init__(self, path: str):
        self.location = os.path.abspath(path.replace('file://localhost', ''))
        self.trackID = ''
        self.averageBpm = ''
        self.dateAdded = ''
        self.playCount = ''
        self.tonality = ''
        self.hot_cues = []
        self.__markers = {}

    def add_hot_cue(self, hot_cue: HotCue):
        self.hot_cues.append(hot_cue)

    def append_markers(self, source_name: str, tags: list):
        self.__markers[source_name] = tags

    def get_markers(self, source_name: str):
        return self.__markers[source_name]
