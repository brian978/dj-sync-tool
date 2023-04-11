from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.ColorEntry import ColorEntry
from app.models.serato.Entry import Entry
from app.models.serato.EntryType import EntryType
from app.models.serato.TypeMap import TypeMap
from app.readers.rekordbox.XmlReader import XmlReader
from app.readers.serato.GEOBReader import GEOBReader
from app.utils.colors import rgb_to_hex
from app.writers.serato.GEOBWriter import GEOBWriter

reader = XmlReader(path='var/rekordbox.xml')
writer = GEOBWriter()

files = reader.read()

geob_reader = GEOBReader(files)
current_entries = geob_reader.read()


def create_empty_color():
    return ColorEntry(*[
        bytes.fromhex(rgb_to_hex(255, 255, 255)),
    ])


def create_empty(type):
    return Entry(*[
        False,
        None,
        False,
        None,
        b'\x00\x7f\x7f\x7f\x7f\x7f',
        bytes.fromhex(rgb_to_hex(0, 0, 0)),
        type,
        0
    ])


for file in files:
    entries = []
    assert isinstance(file, MusicFile)

    # Create list of empty Entries
    for item in range(0, 15):
        if item <= 4:
            entry = create_empty(EntryType.INVALID)
        elif item == 14:
            entry = create_empty_color()
        else:
            entry = create_empty(EntryType.LOOP)

        entries.append(entry)

    # We need to create hot cues for the first 5 Entries (0 to 4)
    for idx, entry in enumerate(entries):
        for hot_cue in file.hot_cues:
            assert isinstance(hot_cue, HotCue)

            if hot_cue.index == idx:
                match hot_cue.type:
                    case HotCueType.CUE:
                        entry.add_hot_cue(
                            hot_cue.start,
                            rgb_to_hex(hot_cue.color[0], hot_cue.color[1], hot_cue.color[2])
                        )

    # Loops will be created on the next 5 (05 - 13)
    tmp_cues = file.hot_cues
    for idx, entry in enumerate(entries):
        if idx < 5 or idx > 14:
            continue

        if len(tmp_cues) == 0:
            break

        hot_cue = tmp_cues.pop(0)
        assert isinstance(hot_cue, HotCue)
        if hot_cue.type != HotCueType.LOOP:
            continue

        entry.set_cue_loop(
            hot_cue.start,
            hot_cue.end
        )

    writer.export(file, entries)

geob_reader = GEOBReader(reader.read())
final = geob_reader.read()
print(1)
