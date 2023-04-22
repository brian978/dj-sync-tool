from app.models.serato.BpmMarkerModel import BpmMarkerModel


def read_bytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


def get_entry_name(fp) -> str:
    entry_name = b''
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            return entry_name.decode('utf-8')

        entry_name += x

    return ''


def split_string(string: bytes, after: int = 72, delimiter: bytes = b'\n'):
    pieces = []
    while len(string) > 0:
        pieces.append(string[:after])
        string = string[after:]

    return delimiter.join(pieces)


def join_string(string: bytes, delimiter: bytes = b'\n'):
    return b''.join(string.split(delimiter))


def calculate_bpm(marker: BpmMarkerModel, next_marker: BpmMarkerModel):
    first_beat_time = marker.get_position()
    next_beat_time = next_marker.get_position()
    total_beats = marker.beats_till_next_marker
    beat_length = (next_beat_time - first_beat_time) / total_beats

    bpm = 60_000 / beat_length
    return bpm
