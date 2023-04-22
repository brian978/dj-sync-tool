class Tempo:
    def __init__(self):
        self.__position: float | None = None
        self.__bpm: float | None = None

    def __repr__(self):
        return 'BPM: {bpm} starting @ {position}'.format(
            bpm=str(self.__bpm).ljust(5),
            position=self.__format_position()
        )

    def __format_position(self):
        if self.__position < 0:
            return self.__position

        # define the number of seconds
        seconds = self.__position / 1000

        # split into minutes, seconds, and milliseconds
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        # print the result in "mm:ss.mmm" format
        return f"{minutes:02d}:{remaining_seconds:02d}:{milliseconds:03d}"

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
