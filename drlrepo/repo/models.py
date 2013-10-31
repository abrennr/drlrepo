from django.db import models
from eulfedora.models import DigitalObject, FileDatastream, FileDatastream, RdfDatastream
from islandora_models import IslandoraAudio, IslandoraBasicImage, IslandoraLargeImage, IslandoraBook, IslandoraPage, IslandoraNewspaperIssue, IslandoraPDF, IslandoraVideo 


class PittBook(IslandoraBook):
    thumbnail_large = FileDatastream("TN_LARGE", "Thumbnail - Large", defaults={
        'mimetype': 'image/jpg',
    })
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
    thumbnail_large = FileDatastream("TN_LARGE", "Thumbnail - Large", defaults={
        'mimetype': 'image/jpg',
    })
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
    fits = FileDatastream("FITS", "FITS", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })

class PittPage(IslandoraPage):
    fits = FileDatastream("FITS", "FITS", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })

class PittNewspaperIssue(IslandoraNewspaperIssue):
    thumbnail_large = FileDatastream("TN_LARGE", "Thumbnail - Large", defaults={
        'mimetype': 'image/jpg',
    })
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
    thumbnail_large = FileDatastream("TN_LARGE", "Thumbnail - Large", defaults={
        'mimetype': 'image/jpg',
    })
    target = FileDatastream("TARGET", "Scanning Target", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
    fits = FileDatastream("FITS", "FITS", defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })
