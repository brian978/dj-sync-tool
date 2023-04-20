import os.path
from xml.dom import minidom
from xml.dom.minidom import Element

from app.models.PlaylistModel import PlaylistModel
from app.models.rekordbox.Track import Track
from app.readers.BaseReader import BaseReader


class TrackReader(BaseReader):
    def __init__(self, path):
        self.__path = os.path.abspath(path)
        self.__playlist: PlaylistModel | None = None

    def read(self):
        files = []
        collection = minidom.parse(self.__path).getElementsByTagName('COLLECTION')[0]
        for node in collection.childNodes:
            if not isinstance(node, Element) or node.nodeName != 'TRACK' or not self.__allowed_track(node):
                continue

            files.append(Track(node).decode())

        return files

    def __allowed_track(self, node: Element):
        return self.__playlist.has_track(int(node.attributes['TrackID'].value))

    def set_playlist(self, playlist: PlaylistModel):
        self.__playlist = playlist
