class Tempo:
    def __init__(self):
        self.__position: float | None = None
        self.__bpm: float | None = None

    def __repr__(self):
        return 'BPM: {bpm} starting @ {position}'.format(
            position=self.__position,
            bpm=str(self.__bpm).ljust(5)
        )

    def set_position(self, value: float):
        # Starting positions for beat grids cannot be negative
        # Serato sets the as negative sometimes, but EVEN IT CANNOT SET a cue point on a negative beat marker
        # self.__position = round((value if value >= 0 else 0) * 1000, 3)
        self.__position = round(value * 1000, 3)

    def set_bpm(self, value: float):
        self.__bpm = round(value, 2)

    def get_position(self):
        return self.__position

    def get_bpm(self):
        return self.__bpm

    def get_beat_length(self):
        return (60 / self.__bpm) * 1000
