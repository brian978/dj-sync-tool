from app.readers.rekordbox.XmlReader import XmlReader

reader = XmlReader(path='var/rekordbox.xml')

files = reader.read()

