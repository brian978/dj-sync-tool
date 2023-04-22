import enum

from app.models.PlaylistModel import PlaylistModel


class CliColor(enum.StrEnum):
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __str__(self):
        return self.value


def color_print(color: CliColor, message: str):
    print(color_msg(color, message))


def color_msg(color: CliColor, message: str):
    return color + message + CliColor.RESET


def pick_playlist(options: list[PlaylistModel]):
    print("Playlists:")

    for idx, element in enumerate(options):
        print("{}) {}".format(idx + 1, element.name))

    i = input("Which playlist do you want to sync?: ")

    try:
        if 0 < int(i) <= len(options):
            return options[int(i) - 1]
    except KeyError:
        print("Option is invalid")

    return None
