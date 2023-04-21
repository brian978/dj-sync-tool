from app.utils.colors import rgb_to_hex


class HotCue:
    def __init__(self):
        self.name = None
        self.start = None
        self.end = None
        self.index = 0
        self.type = None
        self.offsets = dict()

        self.__color: list[int] = []

    def apply_offset(self, offset: int):
        if self.start is not None:
            self.start += offset
            if self.start < 0:
                raise self.__value_error('Start time', self.start)

        if self.end is not None:
            self.end += offset
            if self.end < 0:
                raise self.__value_error('End time', self.end)

    def hex_color(self):
        return rgb_to_hex(self.__color[0], self.__color[1], self.__color[2])

    def set_color(self, color: list[int]):
        self.__color = color

    @staticmethod
    def __value_error(offset_name, offset):
        return ValueError(f'{offset_name} cannot go below 0. Time: {offset}')
