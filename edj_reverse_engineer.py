import json
import os
import sqlite3
import struct
import zlib


# Function to decompress the BLOB data
def decompress_blob(blob):
    # Extract the uncompressed data length (first 4 bytes, big-endian)
    uncompressed_length = struct.unpack('>I', blob[:4])[0]
    # Extract the compressed data (remaining bytes)
    compressed_data = blob[4:]
    # Decompress the data using zlib
    uncompressed_data = zlib.decompress(compressed_data)
    return uncompressed_data


# Function to swap endianness of a double
def swap_endianness_double(data, offset):
    double_bytes = data[offset:offset + 8]
    swapped_double_bytes = double_bytes[::-1]  # Reverse the byte order
    return struct.unpack('<d', swapped_double_bytes)[0]  # Interpret as little-endian double


# Function to decode the beatData structure
def decode_beat_data(data):
    # Initialize offset for parsing
    offset = 0

    # Extract Sample Rate (little-endian double, 8 bytes)
    sample_rate = swap_endianness_double(data, offset)
    offset += 8

    # Extract Track Length (little-endian double, 8 bytes)
    track_length = swap_endianness_double(data, offset)
    offset += 8

    # Extract Is Beat Data Set (byte, 1 byte)
    is_beat_data_set = struct.unpack_from('B', data, offset)[0]
    offset += 1

    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Track Length: {track_length} samples")

    # Calculate track length in seconds accurately
    track_length_seconds = track_length / sample_rate
    minutes = int(track_length_seconds // 60)
    seconds = track_length_seconds % 60

    print(f"Track Length: {minutes} minutes and {seconds:.2f} seconds")
    print(f"Is Beat Data Set: {is_beat_data_set}")

    # Function to parse a single beat grid
    def parse_beat_grid(data, offset):
        # Extract number of beat markers (int, 4 bytes)
        num_markers = struct.unpack_from('>i', data, offset)[0]
        offset += 4

        print(f"Number of Beat Markers: {num_markers}")

        markers = []
        for i in range(num_markers):
            # Each marker contains:
            # - Sample Offset (little-endian double, 8 bytes)
            # - Beat Index (int, 4 bytes)
            sample_offset = swap_endianness_double(data, offset)
            offset += 8
            beat_index = struct.unpack_from('>i', data, offset)[0]
            offset += 4
            markers.append((sample_offset, beat_index))
            print(f"Marker {i}: Sample Offset = {sample_offset} samples, Beat Index = {beat_index}")

        return markers, offset

    # Parse the default beat grid
    print("Default Beat Grid:")
    default_beat_grid, offset = parse_beat_grid(data, offset)

    # Parse the adjusted beat grid
    print("Adjusted Beat Grid:")
    adjusted_beat_grid, offset = parse_beat_grid(data, offset)

    return {
        "sample_rate": sample_rate,
        "track_length": track_length,
        "track_length_seconds": track_length_seconds,
        "is_beat_data_set": is_beat_data_set,
        "default_beat_grid": default_beat_grid,
        "adjusted_beat_grid": adjusted_beat_grid
    }


# Function to convert color components to HEX format
def color_to_hex(red, green, blue):
    return f"{red:02X}{green:02X}{blue:02X}"


# Function to decode the quickCues structure
def decode_quick_cues(data):
    # Initialize offset for parsing
    offset = 0

    # Extract Number of Hot Cues (uint64, 8 bytes, big-endian)
    num_hot_cues = struct.unpack_from('>Q', data, offset)[0]
    offset += 8

    hot_cues = []

    for _ in range(num_hot_cues):
        # Extract Hot Cue Label Length (byte, 1 byte)
        label_length = struct.unpack_from('B', data, offset)[0]
        offset += 1

        # Extract Hot Cue Label (char * N, variable length)
        label = ""
        if label_length > 0:
            label = data[offset:offset + label_length].decode('utf-8')
            offset += label_length

        # Extract Hot Cue Position (little-endian double, 8 bytes)
        position = swap_endianness_double(data, offset)
        offset += 8

        # Extract Hot Cue Colour (4 bytes: alpha, red, green, blue)
        alpha = struct.unpack_from('B', data, offset)[0]
        offset += 1
        red = struct.unpack_from('B', data, offset)[0]
        offset += 1
        green = struct.unpack_from('B', data, offset)[0]
        offset += 1
        blue = struct.unpack_from('B', data, offset)[0]
        offset += 1

        # Convert color to HEX format
        hex_color = color_to_hex(red, green, blue)

        # We need to move the offset along otherwise we might get weird values
        if position == -1:
            continue

        hot_cues.append({
            "label_length": label_length,
            "label": label,
            "position": position,
            "color": hex_color
        })

    print(f"Number of Hot Cues: {len(hot_cues)}")

    # Extract Main Cue Position (little-endian double, 8 bytes)
    main_cue_position = swap_endianness_double(data, offset)
    offset += 8

    # Extract Whether Main Cue Position is Overridden (byte, 1 byte)
    main_cue_override = struct.unpack_from('B', data, offset)[0]
    offset += 1

    # Extract Default Auto-Detected Cue Position (little-endian double, 8 bytes)
    default_cue_position = swap_endianness_double(data, offset)
    offset += 8

    return {
        "num_hot_cues": len(hot_cues),
        "hot_cues": hot_cues,
        "main_cue_position": main_cue_position,
        "main_cue_override": main_cue_override,
        "default_cue_position": default_cue_position
    }


db_path = '~/Music/Engine Library/Database2/m.db'

# Connect to the rbm.db file
conn = sqlite3.connect(os.path.abspath(os.path.expanduser(db_path)))
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

# Query the desired columns
cursor.execute("SELECT * FROM Track WHERE id = 9710")

rows = cursor.fetchall()

for row in rows:
    row = dict(row)
    if row["beatData"] is None:
        continue

    print(f"Track name: {row['title']}")

    # Byte data extracted from the database
    beat_data = decode_beat_data(decompress_blob(row["beatData"]))
    decoded_quick_cues = decode_quick_cues(decompress_blob(row["quickCues"]))

    print(json.dumps(decoded_quick_cues, indent=2))

conn.close()
