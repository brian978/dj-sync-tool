from app.readers.rekordbox.XmlReader import XmlReader
from app.services.FileManagerService import FileManagerService
from app.services.marker.serato.MarkerExtractorService import MarkerExtractorService
from app.services.marker.serato.v2.MarkerExtractorService import MarkerExtractorService as MarkerExtractorServiceV2
from app.services.marker.serato.MarkerWriterService import MarkerWriterService

reader = XmlReader(path='var/rekordbox.xml')

file_manager = FileManagerService(reader)
file_manager.add_extractor(MarkerExtractorService())
file_manager.add_extractor(MarkerExtractorServiceV2())
file_manager.add_writer(MarkerWriterService())

files = file_manager.find_all()

file_manager.write_tags(files)
