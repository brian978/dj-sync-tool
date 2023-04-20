from app.readers.rekordbox.PlaylistReader import PlaylistReader
from app.readers.rekordbox.TrackReader import TrackReader
from app.services.FileManagerService import FileManagerService
from app.services.beatgrid.serato.BeatgridExtractorService import BeatgridExtractorService
from app.services.marker.serato.MarkerExtractorService import MarkerExtractorService
from app.services.marker.serato.v2.MarkerExtractorService import MarkerExtractorService as MarkerExtractorServiceV2
from app.services.marker.serato.MarkerWriterService import MarkerWriterService
from app.services.marker.serato.v2.MarkerWriterService import MarkerWriterService as MarkerWriterServiceV2
from app.utils.prompt import pick_playlist

xml_file = 'tests/fixtures/rekordbox.xml'

# Playlist filter to allow for syncing only specific playlist
playlist_reader = PlaylistReader(path=xml_file)
playlists = playlist_reader.read()

track_reader = TrackReader(path=xml_file)
track_reader.set_playlist(pick_playlist(playlists))

file_manager = FileManagerService(track_reader)

# Serato Beatgrid -- extractor info is populated in order of registration
file_manager.add_extractor(BeatgridExtractorService())

# Serato Markers_
file_manager.add_extractor(MarkerExtractorService())
file_manager.add_writer(MarkerWriterService())

# Serato Markers2
file_manager.add_extractor(MarkerExtractorServiceV2())
file_manager.add_writer(MarkerWriterServiceV2())

# Save to files
file_manager.write_tags(file_manager.extract_tags())
