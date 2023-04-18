import os.path
from xml.dom import minidom
from xml.dom.minidom import Element

from app.models.rekordbox.Track import Track
from app.readers.ReaderInterface import ReaderInterface


class XmlReader(ReaderInterface):
    def __init__(self, path):
        self.__path = os.path.abspath(path)

    def read(self):
        files = []
        collection = minidom.parse(self.__path).getElementsByTagName('COLLECTION')[0]
        for node in collection.childNodes:
            if not isinstance(node, Element) or node.nodeName != 'TRACK':
                continue

            track = Track(node)
            files.append(track.decode())

        return files
