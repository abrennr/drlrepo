import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
from eulfedora.server import Repository
from eulxml.xmlmap.dc import DublinCore
from eulxml.xmlmap.mods import MODS 
import eulxml.xmlmap
from drlrepo.ingest.models import BaseIngestObject 
import drlrepo.ingest.utils
import logging
import logging.config
import bagit
import time
from rdflib import RDFS, Literal, Namespace

repo = Repository()
logging.config.fileConfig('logging.conf')

logger = logging.getLogger('ingestLogger')

def handle_image_object(obj, o):
    obj.obj.content = open(o.obj_path)
    obj.obj.label = o.obj_label 
    obj.jp2.content = open(o.jp2_path)
    obj.jp2.label = o.jp2_label 
    if o.fits_path:
        obj.fits.content = open(o.fits_path)
        obj.fits.label = o.fits_label 
    obj.save()

def handle_paged_object(obj, o):
    # mets 
    obj.mets.content = open(o.mets_path)
    obj.mets.label = o.mets_label 
    # marcxml
    if o.marcxml_label:
        obj.marcxml.content = open(o.marcxml_path)
        obj.marcxml.label = o.marcxml_label 
    # TODO: pdf
    # pages
    for page in o.pages:
        handle_page_object(obj, page)
        time.sleep(.5)
    obj.save()

def handle_page_object(obj, page):
    """
    The page object gets some extra relationships as a member of a book object.
    It should also get:
        - MODS (this should be based on parent book mods, but with page label from METS structmap)
        - JP2 (derived from TIFF)
        - FITS  
        - OCR, if available
    """
    previous = repo.get_object(pid=page.pid)
    if previous.exists:
        repo.purge_object(page.pid)
    page_obj = repo.get_object(pid=page.pid, type=page.fedora_type, create=True)
    page_obj.label = page.label
    page_obj.obj.content = open(page.obj_path)
    page_obj.obj.label = page.obj_label 
    page_obj.jp2.content = open(page.jp2_path)
    page_obj.jp2.label = page.jp2_label 
    if page.ocr_path:
        page_obj.ocr.content = open(page.ocr_path)
        page_obj.ocr.label = page.ocr_label 
    if page.fits_path:
        page_obj.fits.content = open(page.fits_path)
        page_obj.fits.label = page.fits_label 
    page_obj.thumbnail.content = open(page.thumbnail_path)
    page_obj.thumbnail.label = page.thumbnail_label 
    page_obj.save()

    # RELS-INT
    # include height and width of JP2 datastream
    [this_width, this_height] = drlrepo.ingest.utils.get_image_dimensions(page.jp2_path) 
    jp2_uri = page_obj.uriref + u'/JP2'
    ISLANDORA_NS = Namespace(u'http://islandora.ca/ontology/relsext#')
    ISLANDORA_NS.width
    ISLANDORA_NS.height
    page_obj.rels_int.content.add((jp2_uri, ISLANDORA_NS.width, Literal(this_width)))
    page_obj.rels_int.content.add((jp2_uri, ISLANDORA_NS.height, Literal(this_height)))
    page_obj.save(logMessage="setting RELS-INT info")
    
    # clean up
    page.remove_ocr()

    # RELS-EXT

    isPageOf = 'http://islandora.ca/ontology/relsext#isPageOf'
    page_obj.add_relationship(isPageOf, str(obj.uri))

    isMemberOf = 'info:fedora/fedora-system:def/relations-external#isMemberOf'
    page_obj.add_relationship(isMemberOf, str(obj.uri))

    isPageNumber = 'http://islandora.ca/ontology/relsext#isPageNumber'
    page_obj.add_relationship(isPageNumber, page.label)

    # should the page number be a counter here instead of int(page_basename)?
    isSequenceNumber = 'http://islandora.ca/ontology/relsext#isSequenceNumber'
    page_obj.add_relationship(isSequenceNumber, page.seq)

    isSection = 'http://islandora.ca/ontology/relsext#isSection'
    page_obj.add_relationship(isSection, '1')

    logger.info('ingested %s', page.label)

def ingest_item(bag_path):
    bag = bagit.Bag(bag_path)
    # real simple validation check for now
    if not bag.is_valid():
        logger.critical('bag %s failed validation check. Exiting.', bag_path)
        sys.exit(0)
    o = BaseIngestObject(bag_path)
    # check if item already exists.  For now, purge pre-existing versions
    previous = repo.get_object(pid=o.pid)
    if previous.exists:
        repo.purge_object(o.pid)
    obj = repo.get_object(pid=o.pid, create=True, type=o.fedora_type)
    obj.label = o.label
    # mods
    #obj.mods.content = open(o.mods_path)
    obj.mods.content = eulxml.xmlmap.load_xmlobject_from_file(o.mods_path, xmlclass=MODS)
    obj.mods.label = o.mods_label 
    # dc
    obj.dc.content = eulxml.xmlmap.load_xmlobject_from_file(o.dc_path, xmlclass=DublinCore)
    obj.dc.label = o.dc_label 
    # thumb
    obj.thumbnail.content = open(o.thumbnail_path)
    obj.thumbnail.label = o.thumbnail_label 
    # large thumb
    obj.thumbnail_large.content = open(o.thumbnail_large_path)
    obj.thumbnail_large.label = o.thumbnail_large_label 
    # target
    if o.target_label:
        obj.target.content = open(o.target_path)
        obj.target.label = o.target_label 
    # initial save
    obj.save()
    time.sleep(.5)
        
    # RELS-EXT
    # collection isMemberOf
    for collection_pid in o.fedora_collections:
        isMemberOfCollection = 'info:fedora/fedora-system:def/relations-external#isMemberOfCollection'
        parent_uri = "info:fedora/%s" % (collection_pid,)
        obj.add_relationship(isMemberOfCollection, str(parent_uri))
    for site_pid in o.fedora_sites:
        isMemberOfSite = 'http://digital.library.pitt.edu/ontology/relations#isMemberOfSite'
        parent_uri = "info:fedora/%s" % (site_pid,)
        obj.add_relationship(isMemberOfSite, str(parent_uri))

    # handle different types:
    if o.type == 'image' or o.type == 'map':
        handle_image_object(obj, o)
    elif 'text' in o.type or 'manuscript' in o.type or 'newspaper' in o.type:
        handle_paged_object(obj, o)
    else:
        logger.error('WARNING: %s not recognized item type for %s', o.type, o.pid)
    # clean up
    o.remove_thumbnail()

if __name__ == '__main__':
    bag_path = sys.argv[1]
    logger.debug('working with %s', bag_path)
    ingest_item(bag_path)
    logger.info('%s ingested OK', bag_path)
