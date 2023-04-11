from app.models.HotCue import HotCue


class Track:
    def __init__(self, track):
        self.__track = track

    def attr(self, name):
        return self.__track.attributes[name].value

    def hot_cues(self):
        cues = self.__track.getElementsByTagName("POSITION_MARK")
        for xml_cue in cues:
            hot_cue = HotCue()
            hot_cue.name = xml_cue.attributes["Name"].value
            hot_cue.start = float(xml_cue.attributes["Start"].value) * 1000  # need value in milliseconds
            hot_cue.end = float(xml_cue.attributes["End"].value) * 1000      # need value in milliseconds
            hot_cue.index = int(xml_cue.attributes["Num"].value)
            hot_cue.color = [
                xml_cue.attributes["Red"].value,
                xml_cue.attributes["Green"].value,
                xml_cue.attributes["Blue"].value
            ]

            yield hot_cue
