from django.db import models
from eulfedora.models import DigitalObject, FileDatastream, FileDatastream, RdfDatastream
from islandora_models import IslandoraAudio, IslandoraBasicImage, IslandoraLargeImage, IslandoraBook, IslandoraPage, IslandoraNewspaperIssue, IslandoraPDF, IslandoraVideo 


class PittBook(IslandoraBook):
    marcxml = FileDatastream("MARCXML", "MARCXML", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })
    mets = FileDatastream("METS", "METS XML", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })

class PittBasicImage(IslandoraBasicImage):
    pass

class PittPage(IslandoraPage):
    pass

class PittNewspaperIssue(IslandoraNewspaperIssue):
    pass

class PittLargeImage(IslandoraLargeImage):
    kml = FileDatastream("KML", "KML data", defaults={
        'versionable': False,
        'mimetype': 'text/xml',
    })

