from app.models.Offset import Offset
from app.utils.colors import rgb_to_hex


class HotCue:
    def __init__(self):
        self.name = None
        self.start = None
        self.end = None
        self.index = 0
        self.type = None
        self.offset: Offset | None = None
        self.__color: list[int] = []

    def __repr__(self):
        return '{index}) Name: `{name}` | Start: {start}{end}'.format(
            name=self.name.ljust(20) if len(self.name) > 0 else self.name,
            index=self.index,
            start=str(f'{self.start}ms').ljust(10),
            end=str(f' | End: {self.end}ms').ljust(10) if self.end is not None else ''
        )

    def hex_color(self):
        return rgb_to_hex(self.__color[0], self.__color[1], self.__color[2])

    def set_color(self, color: list[int]):
        self.__color = color

    def apply_offset(self):
        if self.offset is None:
            return

        self.__update_positions(int(self.offset.get_value()))

    def revert_offset(self):
        if self.offset is None:
            return

        self.__update_positions(-int(self.offset.get_value()))

    def __update_positions(self, offset: int):
        if self.start is not None:
            self.start += offset
            if self.start < 0:
                raise self.__value_error('Start time', self.start)

        if self.end is not None:
            self.end += offset
            if self.end < 0:
                raise self.__value_error('End time', self.end)

    @staticmethod
    def __value_error(offset_name, offset):
        return ValueError(f'{offset_name} cannot go below 0. Time: {offset}')
