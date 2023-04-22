class Offset:
    def __init__(self, source_beat: float, dest_beat: float):
        self.__source_beat: float = source_beat  # value in ms
        self.__dest_beat: float = dest_beat  # value in ms

    def __repr__(self):
        return 'Offset: `{value}` | Source beat: {src_bt} | Destination beat: {dst_bt}'.format(
            value=str(f'{int(self.get_value())}ms').ljust(7),
            src_bt=str(f'{int(self.__source_beat)}ms').ljust(7),
            dst_bt=str(f'{int(self.__dest_beat)}ms').ljust(7)
        )

    def distance_to_source(self, number: float):
        return abs(self.__source_beat - number)

    def get_value(self) -> int:
        """
        :return: int Value of the offset in milliseconds
        """
        if self.__dest_beat < 0:
            diff = self.__source_beat - abs(self.__dest_beat)
        else:
            diff = abs(self.__dest_beat - self.__source_beat)

        return int(diff if self.__source_beat < self.__dest_beat else -diff)
