from datetime import datetime

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.rekordbox.PositionMarkType import PositionMarkType
from app.models.rekordbox.TypeMap import TypeMap


class Track:
    def __init__(self, track):
        self.__track = track

    def decode(self):
        music_file = MusicFile(self.__attr("Location"))
        music_file.trackID = self.__attr("TrackID")
        music_file.averageBpm = float(self.__attr("AverageBpm"))
        music_file.dateAdded = datetime.strptime(self.__attr("DateAdded"), '%Y-%m-%d')
        music_file.playCount = int(self.__attr("PlayCount"))
        music_file.tonality = self.__attr("Tonality")

        for hot_cue in self.__hot_cues():
            music_file.add_hot_cue(hot_cue)

        return music_file

    def __attr(self, name):
        return self.__track.attributes[name].value

    def __hot_cues(self):
        cues = self.__track.getElementsByTagName("POSITION_MARK")
        for xml_cue in cues:
            # figure out a way to have a pool of indexes so that we will the remaining
            # hot cues with memory cues (if available)
            index = int(xml_cue.attributes["Num"].value)
            cue_type = self.__cue_type(index, xml_cue)

            hot_cue = HotCue()
            hot_cue.type = cue_type
            hot_cue.name = xml_cue.attributes["Name"].value
            hot_cue.start = int(float(xml_cue.attributes["Start"].value) * 1000)  # need value in milliseconds
            hot_cue.index = index
            hot_cue.color = self.__cue_color(cue_type, xml_cue)

            # Only loops have an "End" attribute
            if cue_type == HotCueType.LOOP:
                hot_cue.end = int(float(xml_cue.attributes["End"].value) * 1000)  # need value in milliseconds

            yield hot_cue

    @staticmethod
    def __cue_type(index, xml_cue) -> PositionMarkType:
        cue_type = int(xml_cue.attributes["Type"].value)
        if index < 0:
            cue_type = PositionMarkType.MEMORY.value

        return TypeMap.from_rb(PositionMarkType.parse(cue_type))

    @staticmethod
    def __cue_color(cue_type, xml_cue):
        if cue_type == PositionMarkType.MEMORY:
            return [255, 255, 255]

        return [
            int(xml_cue.attributes["Red"].value),
            int(xml_cue.attributes["Green"].value),
            int(xml_cue.attributes["Blue"].value)
        ]
