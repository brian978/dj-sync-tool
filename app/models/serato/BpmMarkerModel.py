from app.models.Tempo import Tempo


class BpmMarkerModel(Tempo):
    def __init__(self, position: float, bpm: float, beats_till_next_marker: int | None = None):
        super().__init__()
        self.set_position(float(position))
        self.set_bpm(float(bpm))
        self.beats_till_next_marker = beats_till_next_marker
