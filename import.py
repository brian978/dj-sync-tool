from app.readers.rekordbox.XmlReader import XmlReader
from app.services.FileManagerService import FileManagerService
from app.services.beatgrid.serato.BeatgridExtractorService import BeatgridExtractorService
from app.services.marker.serato.MarkerExtractorService import MarkerExtractorService
from app.services.marker.serato.v2.MarkerExtractorService import MarkerExtractorService as MarkerExtractorServiceV2
from app.services.marker.serato.MarkerWriterService import MarkerWriterService
from app.services.marker.serato.v2.MarkerWriterService import MarkerWriterService as MarkerWriterServiceV2

reader = XmlReader(path='tests/fixtures/rekordbox.xml')

file_manager = FileManagerService(reader)

# Serato Markers_
file_manager.add_extractor(MarkerExtractorService())
file_manager.add_writer(MarkerWriterService())

# Serato Markers2
file_manager.add_extractor(MarkerExtractorServiceV2())
file_manager.add_writer(MarkerWriterServiceV2())

# Serato Beatgrid
file_manager.add_extractor(BeatgridExtractorService())

# Save to files
file_manager.write_tags(file_manager.find_all())
