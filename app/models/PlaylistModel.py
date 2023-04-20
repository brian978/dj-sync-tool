class PlaylistModel:
    def __init__(self, name: str):
        self.name = name
        self.tracks: list[int] = list()

    def add_track(self, track_id: int):
        self.tracks.append(track_id)

    def has_track(self, track_id: int):
        return track_id in self.tracks
