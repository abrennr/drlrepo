import sys
import os
sys.path.append('/home/abrenner/django/drlrepo')
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
from eulfedora.server import Repository
from eulxml.xmlmap.dc import DublinCore
import eulxml.xmlmap
from drlrepo.ingest.models import BaseIngestObject 

repo = Repository()

def handle_image_object(obj, o):
    obj.obj.content = open(o.obj_path)
    obj.obj.label = o.obj_label 
    obj.jp2.content = open(o.jp2_path)
    obj.jp2.label = o.jp2_label 
    if o.jp2_is_temp:
        o.remove_jp2()
    # TODO: MIX
    return obj

def handle_paged_object(obj, o):
    # mets 
    obj.mets.content = open(o.mets_path)
    obj.mets.label = o.mets_label 
    # marcxml
    if o.marcxml_path:
        obj.marcxml.content = open(o.marcxml_path)
        obj.marcxml.label = o.marcxml_label 
    # TODO: pdf
    # pages
    for page in o.pages:
        handle_page_object(obj, page)
    return obj

def handle_page_object(obj, page):
    """
    The page object gets some extra relationships as a member of a book object.
    It should also get:
        - MODS (this should be based on parent book mods, but with page label from METS structmap)
        - JP2 (derived from TIFF)
        - MIX
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
    page_obj.thumbnail.content = open(page.thumbnail_path)
    page_obj.thumbnail.label = page.thumbnail_label 
    page_obj.save()
    # TODO: mix
    # clean up
    page.remove_thumbnail()
    page.remove_ocr()
    if page.jp2_is_temp:
        page.remove_jp2()

    # RELS-EXT

    isPageNumber = 'http://islandora.ca/ontology/relsext#isPageNumber'
    page_obj.add_relationship(isPageNumber,  page.label)

    # should the page number be a counter here instead of int(page_basename)?
    isSequenceNumber = 'http://islandora.ca/ontology/relsext#isSequenceNumber'
    page_obj.add_relationship(isSequenceNumber,  page.seq)

    isSection = 'http://islandora.ca/ontology/relsext#isSection'
    page_obj.add_relationship(isSection, '1')

    isPageOf = 'http://islandora.ca/ontology/relsext#isPageOf'
    page_obj.add_relationship(isPageOf, obj.uri)

    isMemberOf = 'info:fedora/fedora-system:def/relations-external#isMemberOf'
    page_obj.add_relationship(isMemberOf, obj.uri)



def ingest_item(item_id):
    o = BaseIngestObject(item_id)
    # check if item already exists.  For now, purge pre-existing versions
    previous = repo.get_object(pid=o.pid)
    if previous.exists:
        repo.purge_object(o.pid)
    obj = repo.get_object(pid=o.pid, create=True, type=o.fedora_type)
    obj.label = o.label
    # mods
    obj.mods.content = open(o.mods_path)
    obj.mods.label = o.mods_label 
    # dc
    obj.dc.content = eulxml.xmlmap.load_xmlobject_from_file(o.dc_path, xmlclass=DublinCore)
    obj.dc.label = o.dc_label 
    # thumb
    obj.thumbnail.content = open(o.thumbnail_path)
    obj.thumbnail.label = o.thumbnail_label 
    # initial save
    obj.save()
        
    # RELS-EXT
    # collection isMemberOf
    #isMemberOf = 'info:fedora/fedora-system:def/relations-external#isMemberOf'
    #parent_uri = 'info:fedora/%s' % (coll_pid,)
    #obj.add_relationship(isMemberOf, parent_uri)

    # handle different types:
    if o.type == 'image' or o.type == 'map':
        obj = handle_image_object(obj, o)
        obj.save()
    elif 'text' in o.type or 'manuscript' in o.type:
        obj = handle_paged_object(obj, o)
        obj.save()
    else:
        print 'WARNING: %s not recognized item type for %s' % (o.type, o.pid)
    # clean up
    o.remove_thumbnail()

if __name__ == '__main__':
    item_id = sys.argv[1]
    print 'working with %s' % (item_id,)
    ingest_item(item_id)
