import urllib.parse
from datetime import datetime
from xml.dom.minidom import Element

from app.models.HotCue import HotCue
from app.models.MusicFile import MusicFile
from app.models.Tempo import Tempo
from app.models.rekordbox.PositionMarkType import PositionMarkType
from app.models.rekordbox.TypeMap import TypeMap


class Track:
    def __init__(self, track):
        self.__track = track

    def decode(self):
        music_file = MusicFile(urllib.parse.unquote(self.__attr("Location")))
        music_file.trackID = self.__attr("TrackID")
        music_file.averageBpm = float(self.__attr("AverageBpm"))
        music_file.dateAdded = datetime.strptime(self.__attr("DateAdded"), '%Y-%m-%d')
        music_file.playCount = int(self.__attr("PlayCount"))
        music_file.tonality = self.__attr("Tonality")
        music_file.totalTime = self.__attr("TotalTime")

        for hot_cue in self.__hot_cues():
            music_file.add_hot_cue(hot_cue)

        self.__assign_memory_cues(music_file)

        for tempo in self.__beatgrid():
            music_file.add_beatgrid_marker(tempo)

        return music_file

    def __attr(self, name):
        return self.__track.attributes[name].value

    def __hot_cues(self):
        for node in self.__track.childNodes:
            if not isinstance(node, Element) or node.nodeName != 'POSITION_MARK':
                continue

            # figure out a way to have a pool of indexes so that we will the remaining
            # hot cues with memory cues (if available)
            index = int(node.attributes["Num"].value)
            cue_type = self.__cue_type(index, node)

            hot_cue = HotCue()
            hot_cue.type = TypeMap.from_rb(cue_type)
            hot_cue.name = node.attributes["Name"].value
            hot_cue.start = int(float(node.attributes["Start"].value) * 1000)  # need value in milliseconds
            hot_cue.index = index
            hot_cue.set_color(self.__cue_color(cue_type, node))

            # Only loops have an "End" attribute
            if cue_type == PositionMarkType.LOOP:
                hot_cue.end = int(float(node.attributes["End"].value) * 1000)  # need value in milliseconds

            yield hot_cue

    def __beatgrid(self):
        for node in self.__track.childNodes:
            if not isinstance(node, Element) or node.nodeName != 'TEMPO':
                continue

            tempo = Tempo()
            tempo.position = node.attributes["Inizio"].value
            tempo.bpm = node.attributes["Bpm"].value

            yield tempo

    @staticmethod
    def __unassigned_indexes(hot_cues: list[HotCue]):
        # Create a set of all possible index values
        all_indexes = set(range(8))

        # Iterate over the list of objects and remove assigned index values
        for obj in hot_cues:
            if obj.index in all_indexes:
                all_indexes.remove(obj.index)

        # Return the remaining unassigned index values as a set
        return all_indexes

    @staticmethod
    def __cue_type(index, xml_cue) -> PositionMarkType:
        cue_type = int(xml_cue.attributes["Type"].value)
        if index < 0:
            cue_type = PositionMarkType.MEMORY.value

        return PositionMarkType.parse(cue_type)

    @staticmethod
    def __cue_color(cue_type, xml_cue):
        if cue_type == PositionMarkType.MEMORY:
            return [255, 255, 255]

        return [
            int(xml_cue.attributes["Red"].value),
            int(xml_cue.attributes["Green"].value),
            int(xml_cue.attributes["Blue"].value)
        ]

    def __assign_memory_cues(self, file: MusicFile):
        unassigned_indexes = self.__unassigned_indexes(file.hot_cues)
        for hot_cue in file.hot_cues:
            if len(unassigned_indexes) == 0:
                break

            if hot_cue.index < 0:
                hot_cue.index = unassigned_indexes.pop()
                hot_cue.name = f'M: {(hot_cue.name if len(hot_cue.name) > 0 else hot_cue.index)}'
