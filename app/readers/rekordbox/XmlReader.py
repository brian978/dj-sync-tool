from datetime import datetime
import os.path
from xml.dom import minidom

from app.models.MusicFile import MusicFile
from app.models.rekordbox.Track import Track


class XmlReader:
    __path = ''

    def __init__(self, path):
        self.__path = os.path.abspath(path)

    def read(self):
        collection = minidom.parse(self.__path)
        tracks = collection.getElementsByTagName('TRACK')

        files = []
        for xml_track in tracks:
            track = Track(xml_track)
            music_file = MusicFile(track.attr("Location"))
            music_file.trackID = track.attr("TrackID")
            music_file.averageBpm = track.attr("AverageBpm")
            music_file.dateAdded = datetime.strptime(track.attr("DateAdded"), '%Y-%m-%d')
            music_file.playCount = track.attr("PlayCount")
            music_file.tonality = track.attr("Tonality")

            for hot_cue in track.hot_cues():
                music_file.add_hot_cue(hot_cue)

            files.append(music_file)

        return files
