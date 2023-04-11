#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import ast
import configparser
import io
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import enum
import mutagen

FMT_VERSION = 'BB'


class EntryType(enum.IntEnum):
    INVALID = 0
    CUE = 1
    LOOP = 3


def serato32encode(data):
    """Encode 3 byte plain text into 4 byte Serato binary format."""
    a, b, c = struct.unpack('BBB', data)
    z = c & 0x7F
    y = ((c >> 7) | (b << 1)) & 0x7F
    x = ((b >> 6) | (a << 2)) & 0x7F
    w = (a >> 5)
    return bytes(bytearray([w, x, y, z]))


def serato32decode(data):
    """Decode 4 byte Serato binary format into 3 byte plain text."""
    w, x, y, z = struct.unpack('BBBB', data)
    c = (z & 0x7F) | ((y & 0x01) << 7)
    b = ((y & 0x7F) >> 1) | ((x & 0x03) << 6)
    a = ((x & 0x7F) >> 2) | ((w & 0x07) << 5)
    return struct.pack('BBB', a, b, c)


class Entry(object):
    FMT = '>B4sB4s6s4sBB'
    FIELDS = ('start_position_set', 'start_position', 'end_position_set',
              'end_position', 'field5', 'color', 'type', 'is_locked')

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name))
                           for name in self.FIELDS))

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        entry_data = []

        start_position_set = None
        end_position_set = None
        for field, value in zip(cls.FIELDS, info):
            if field == 'start_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                start_position_set = value
            elif field == 'end_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                end_position_set = value
            elif field == 'start_position':
                assert start_position_set is not None
                if start_position_set:
                    value = struct.unpack(
                        '>I', serato32decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'end_position':
                assert end_position_set is not None
                if end_position_set:
                    value = struct.unpack(
                        '>I', serato32decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'color':
                value = serato32decode(value)
            elif field == 'type':
                value = EntryType(value)
            entry_data.append(value)

        return cls(*entry_data)

    def add_hot_cue(self, position, color):
        setattr(self, 'start_position_set', True)
        setattr(self, 'start_position', position)
        setattr(self, 'type', EntryType.CUE)
        setattr(self, 'color', bytes.fromhex(color))

    def set_start_position(self, value):
        setattr(self, 'start_position', value)

    def dump(self):
        entry_data = []
        for field in self.FIELDS:
            value = getattr(self, field)
            if field == 'start_position_set':
                value = 0x7F if not value else 0x00
            elif field == 'end_position_set':
                value = 0x7F if not value else 0x00
            elif field == 'color':
                value = serato32encode(value)
            elif field == 'start_position':
                if value is None:
                    value = 0x7F7F7F7F.to_bytes(4, 'big')
                else:
                    value = serato32encode(struct.pack('>I', value)[1:])
            elif field == 'end_position':
                if value is None:
                    value = 0x7F7F7F7F.to_bytes(4, 'big')
                else:
                    value = serato32encode(struct.pack('>I', value)[1:])
            elif field == 'type':
                value = int(value)
            entry_data.append(value)

        return struct.pack(self.FMT, *entry_data)


class Color(Entry):
    FMT = '>4s'
    FIELDS = ('color',)


def parse(fp):
    assert struct.unpack(FMT_VERSION, fp.read(2)) == (0x02, 0x05)

    num_entries = struct.unpack('>I', fp.read(4))[0]
    for i in range(num_entries):
        entry_data = fp.read(0x16)
        assert len(entry_data) == 0x16

        entry = Entry.load(entry_data)
        yield entry

    yield Color.load(fp.read())


def dump(new_entries):
    data = struct.pack(FMT_VERSION, 0x02, 0x05)
    num_entries = len(new_entries) - 1
    data += struct.pack('>I', num_entries)
    for entry_data in new_entries:
        data += entry_data.dump()
    return data



def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    parser.add_argument('-e', '--edit', action='store_true')
    args = parser.parse_args(argv)

    # if args.edit:
    #     text_editor = shutil.which(os.getenv('EDITOR', 'vi'))
    #     if not text_editor:
    #         print('No suitable $EDITOR found.', file=sys.stderr)
    #         return 1
    #
    #     hex_editor = shutil.which(os.getenv('HEXEDITOR', 'bvi'))
    #     if not hex_editor:
    #         print('No suitable HEXEDITOR found.', file=sys.stderr)
    #         return 1

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            data = tagfile['GEOB:Serato Markers_'].data
        except KeyError:
            print('File is missing "GEOB:Serato Markers_" tag')
            return 1
    else:
        with open(args.file, mode='rb') as fp:
            data = fp.read()

    entries = list(parse(io.BytesIO(data)))
    new_entries = []
    action = None

    width = math.floor(math.log10(len(entries))) + 1
    for entry_index, entry in enumerate(entries):
        if entry_index == 0:
            entry.add_hot_cue(0, 'CC0000')

        if entry_index == 5:
            entry.set_start_position(2463)

        print('{:{}d}: {!r}'.format(entry_index, width, entry))

    if args.edit:
        if new_entries == entries:
            print('No changes made.')
        else:
            save_markers(args.file, tagfile, entries)

    return 0


def save_markers(file, tagfile, entries):
    data = dump(entries)

    if tagfile is not None:
        tagfile['GEOB:Serato Markers_'] = mutagen.id3.GEOB(
            encoding=0,
            mime='application/octet-stream',
            desc='Serato Markers_',
            data=data,
        )
        tagfile.save()
    else:
        with open(file, mode='wb') as fp:
            fp.write(data)


if __name__ == '__main__':
    sys.exit(main())
