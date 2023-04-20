from app.utils.colors import rgb_to_hex


class HotCue:
    def __init__(self):
        self.name = None
        self.start = None
        self.end = None
        self.index = 0
        self.__color: list[int] = []
        self.type = None
        self.offsets = dict()

    def apply_offset(self, offset: int):
        if self.start is not None:
            self.start += offset
            if self.start < 0:
                raise ValueError(f'Cannot go below start time 0')

        if self.end is not None:
            self.end += offset
            if self.end < 0:
                raise ValueError(f'Cannot go below end time 0')

    def hex_color(self):
        return rgb_to_hex(self.__color[0], self.__color[1], self.__color[2])

    def set_color(self, color: list[int]):
        self.__color = color
