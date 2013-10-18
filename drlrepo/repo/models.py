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
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })

class PittBasicImage(IslandoraBasicImage):
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })

class PittPage(IslandoraPage):
    pass

class PittNewspaperIssue(IslandoraNewspaperIssue):
    marcxml = FileDatastream("MARCXML", "MARCXML", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })
    mets = FileDatastream("METS", "METS XML", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })

class PittLargeImage(IslandoraLargeImage):
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
