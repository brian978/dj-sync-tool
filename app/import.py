from app.models.HotCue import HotCue
from app.models.MusicFile import MusicFile
from app.models.serato.Entry import Entry
from app.models.serato.EntryType import EntryType
from app.models.serato.TypeMap import TypeMap
from app.readers.rekordbox.XmlReader import XmlReader
from app.readers.serato.GEOBReader import GEOBReader
from app.utils.colors import rgb_to_hex
from app.writers.serato.GEOBWriter import GEOBWriter

reader = XmlReader(path='var/rekordbox.xml')
writer = GEOBWriter()


def create_empty():
    return Entry(*[
        False,
        None,
        False,
        None,
        b'\x00\x7f\x7f\x7f\x7f\x7f',
        bytes.fromhex(rgb_to_hex(0, 0, 0)),
        EntryType.INVALID,
        0
    ])


for file in reader.read():
    entries = []
    assert isinstance(file, MusicFile)

    # create the entries for Serato
    # We need to create hot cues for the first 5 Entries (0 to 4)
    # Loops will be created on the next 5 (05 - 13)
    for hot_cue in file.hot_cues:
        assert isinstance(hot_cue, HotCue)

        entry_args = [
            True if hot_cue.start is not None else False,
            hot_cue.start if hot_cue.start is not None else None,
            True if hot_cue.end is not None else False,
            hot_cue.start if hot_cue.end is not None else None,
            b'\x00\x7f\x7f\x7f\x7f\x7f',
            bytes.fromhex(rgb_to_hex(hot_cue.color[0], hot_cue.color[1], hot_cue.color[2])),
            TypeMap.to_serato(hot_cue.type),
            0
        ]

        entries.append(Entry(*entry_args))

    # writer.export(file, entries)

geob_reader = GEOBReader(reader.read())
geob_reader.read()
