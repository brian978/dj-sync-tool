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
            files.append(track.decode())

        return files
