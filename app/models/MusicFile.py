import os

from app.models.HotCue import HotCue


class MusicFile:
    trackID = ''
    averageBpm = ''
    dateAdded = ''
    playCount = ''
    location = ''
    tonality = ''

    hot_cues = []

    def __init__(self, path: str):
        self.location = os.path.abspath(path.replace('file://localhost', ''))

    def add_hot_cue(self, hot_cue: HotCue):
        self.hot_cues.append(hot_cue)
