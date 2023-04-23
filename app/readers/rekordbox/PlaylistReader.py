from xml.dom import minidom
from xml.dom.minidom import Element

from app.models.PlaylistModel import PlaylistModel
from app.readers.BaseReader import BaseReader


class PlaylistReader(BaseReader):
    def __init__(self, path):
        super().__init__(path)

    @staticmethod
    def __is_folder(element: Element):
        return element.attributes['Type'].nodeValue == '0'

    def read(self):
        playlists = []
        root_node = minidom.parse(self._path).getElementsByTagName('PLAYLISTS')[0]
        for node in root_node.childNodes:
            if node.attributes is not None and node.attributes['Name'].value == 'ROOT':
                xml_playlists = node.getElementsByTagName('NODE')
                for xml_playlist in xml_playlists:
                    if self.__is_folder(xml_playlist):
                        continue

                    playlist = PlaylistModel(xml_playlist.attributes['Name'].value)
                    xml_tracks = xml_playlist.getElementsByTagName('TRACK')
                    for xml_track in xml_tracks:
                        playlist.add_track(int(xml_track.attributes['Key'].value))

                    playlists.append(playlist)

        return playlists
