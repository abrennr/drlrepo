from django.db import models
from eulfedora.models import DigitalObject, FileDatastream, FileDatastream, RdfDatastream, XmlDatastream
from eulxml.xmlmap.mods import MODS

class IslandoraAudio(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:sp-audioCModel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
    })
    mp3 = FileDatastream("PROXY_MP3", "MP3 derivative", defaults={
        'versionable': False,
    })


class IslandoraBasicImage(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:sp_basic_image'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
    jpg = FileDatastream("MEDIUM_SIZE", "Derivative medium size image", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })

class IslandoraBook(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:bookCModel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ] 
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    pdf = FileDatastream("PDF", "PDF derivative", defaults={
        'versionable': False,
        'mimetype': 'application/pdf',
    })


class IslandoraPage(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:pageCModel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
    pdf = FileDatastream("PDF", "PDF derivative", defaults={
        'versionable': False,
        'mimetype': 'application/pdf',
    })
    jp2 = FileDatastream("JP2", "JP2 derivative", defaults={
        'versionable': False,
        'mimetype': 'image/jp2',
    })
    jpg = FileDatastream("JPG", "JPG derivative", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    ocr = FileDatastream("OCR", "Raw OCR", defaults={
        'versionable': False,
        'mimetype': 'text/plain',
    })
    hocr = FileDatastream("HOCR", "HOCR formatted OCR", defaults={
        'versionable': False,
    })
    rels_int = RdfDatastream("RELS-INT", "RELS-INT") 


class IslandoraLargeImage(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:sp_large_image_cmodel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
        'mimetype': 'image/tiff',
    })
    jp2 = FileDatastream("JP2", "JP2 derivative", defaults={
        'versionable': False,
        'mimetype': 'image/jp2',
    })
    jpg = FileDatastream("JPG", "JPG derivative", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })

class IslandoraNewspaperIssue(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:newspaperIssueCModel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    pdf = FileDatastream("PDF", "PDF derivative", defaults={
        'versionable': False,
        'mimetype': 'application/pdf',
    })

class IslandoraPDF(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:sp_pdf'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
        'mimetype': 'application/pdf',
    })
    preview = FileDatastream("PREVIEW", "Preview Image", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    fulltext = FileDatastream("FULL_TEXT", "Full text of PDF", defaults={
        'versionable': False,
    })

class IslandoraVideo(DigitalObject):
    ISLANDORA_CONTENT_MODEL = 'info:fedora/islandora:sp_videoCModel'
    CONTENT_MODELS = [ ISLANDORA_CONTENT_MODEL ]
    thumbnail = FileDatastream("TN", "Thumbnail", defaults={
        'versionable': False,
        'mimetype': 'image/jpeg',
    })
    mods = XmlDatastream("MODS", "MODS", MODS, defaults={
        'versionable': True,
        'mimetype': 'text/xml',
        'control_group': 'X',
    })
    obj = FileDatastream("OBJ", "Master File", defaults={
        'versionable': True,
    })
    ogg = FileDatastream("OGG", "audio-only derivative in OGG format", defaults={
        'versionable': False,
    })
    mp4 = FileDatastream("MP4", "MP4 derivative", defaults={
        'versionable': False,
    })
    mkv = FileDatastream("MKV", "MKV derivative", defaults={
        'versionable': False,
    })


