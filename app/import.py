from app.readers.rekordbox.XmlReader import XmlReader
from app.readers.serato.GEOBReader import GEOBReader
from app.writers.serato.GEOBWriter import GEOBWriter

reader = XmlReader(path='var/rekordbox.xml')
writer = GEOBWriter(reader)

writer.create_entries()
writer.export()

geob_reader = GEOBReader(reader.read())
final = geob_reader.read()
