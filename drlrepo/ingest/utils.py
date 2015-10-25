import sys
import os
import zipfile
import subprocess
import shutil
import glob
import json
import drlutils.image.utils
import drlrepo.ingest.config
import logging
import urllib2
import requests
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
from eulfedora.server import Repository
from eulxml.xmlmap.dc import DublinCore
from eulxml.xmlmap.mods import MODS 
import eulxml.xmlmap
import drlrepo.repo.models 
from drlrepo.repo.models import PittLargeImage, PittBook, PittPage, PittNewspaperIssue, PittCollection 
"""
Utility script to migrate digital objects from the legacy (as of 2012)
DRL repository to Fedora.

For each object, determine content
type and route to a handler function that will create the object in 
Fedora and upload all relevant datastreams.
"""

# map of legacy item types to eulfedora digital object models 
ITEM_TYPE_CM_MAP = {
    'collection': PittCollection,
    'image': PittLargeImage,
    'text - cataloged': PittBook,
    'text - uncataloged': PittBook,
    'newspaper - cataloged': PittNewspaperIssue,
    'newspaper - uncataloged': PittNewspaperIssue,
    'map': PittLargeImage,
    'manuscript': PittBook,
    'page': PittPage
}


def add_datastream(pid, this_type, ds_id, content, mimetype=None):
    repo = Repository()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.info('working with item %s, datastream %s, content %s' % (pid, ds_id, content))
    type_model = getattr(drlrepo.repo.models, this_type)
    obj = repo.get_object(pid=pid, type=type_model)
    ds_attr = getattr(obj, ds_id)
    if ds_id == 'mods':
        obj.mods.content = eulxml.xmlmap.load_xmlobject_from_file(content, xmlclass=MODS)
    elif ds_id == 'dc':
        obj.dc.content = eulxml.xmlmap.load_xmlobject_from_file(content, xmlclass=DublinCore)
    else:
        ds_attr.content = open(content) 
    ds_attr.label = os.path.basename(content) 
    if mimetype:    
        ds_attr.mimetype = mimetype
    obj.save()


def add_relationship_site(obj_pid, site_obj_pid):
    repo = Repository()
    obj = repo.get_object(pid=obj_pid)
    parent_uri = "info:fedora/%s" % (site_obj_pid,)
    obj.add_relationship(drlrepo.ingest.config.IS_MEMBER_OF_SITE, str(parent_uri))
    obj.save()

def remove_relationship_site(obj_pid, site_obj_pid):
    # eulfedora does not provide a remove relationship method, so direct API call
    rel_subject = u'info:fedora/' +  obj_pid
    rel_predicate = drlrepo.ingest.config.IS_MEMBER_OF_SITE.replace('#', '%23') 
    rel_object = u'info:fedora/' +  site_obj_pid
    api_call_url = '%s/fedora/objects/%s/relationships?subject=%s&predicate=%s&object=%s&isLiteral=false' % (drlrepo.ingest.config.FEDORA_URL, obj_pid, rel_subject, rel_predicate, rel_object)
    r = requests.delete(api_call_url, auth=(drlrepo.ingest.config.FEDORA_USER, drlrepo.ingest.config.FEDORA_PASS))
    if not r.status_code == requests.codes.ok:
        return 1
    return


def add_relationship_collection(obj_pid, collection_obj_pid):
    repo = Repository()
    obj = repo.get_object(pid=obj_pid)
    parent_uri = "info:fedora/%s" % (collection_obj_pid,)
    obj.add_relationship(drlrepo.ingest.config.IS_MEMBER_OF_COLLECTION, str(parent_uri))
    obj.save()

def remove_relationship_collection(obj_pid, collection_obj_pid):
    rel_subject = u'info:fedora/' +  obj_id
    rel_predicate = drlrepo.ingest.config.IS_MEMBER_OF_COLLECTION.replace('#', '%23') 
    rel_object = u'info:fedora/' +  collection_obj_pid
    api_call_url = '%s/fedora/objects/%s/relationships?subject=%s&predicate=%s&object=%s&isLiteral=false' % (drlrepo.ingest.config.FEDORA_URL, obj_pid, rel_subject, rel_predicate, rel_object)
    r = requests.delete(api_call_url, auth=(drlrepo.ingest.config.FEDORA_USER, drlrepo.ingest.config.FEDORA_PASS))
    if not r.status_code == requests.codes.ok:
        return 1
    return
        
def get_image_dimensions(image_path):
    # use exiftool to get image dimensions for specified image
    # exiftool called with -t for tab-delimited output, and
    # only the specified '-ImageSize' tag
    dim = subprocess.Popen([
        drlrepo.ingest.config.EXIFTOOL_PATH,
        '-t',
        '-ImageSize',
        image_path], 
        stdout=subprocess.PIPE)
    # read the line of stdout, strip newline, split on tab,
    # then split on the 'x' height/width separator 
    return dim.stdout.readline().strip().split('\t')[1].split('x')

def get_item_metadata(bag_path):
    metadata_file_lookup = os.path.join(
        bag_path,
        'data',
        '*.drl-admin.json'
    ) 
    matches = glob.glob(metadata_file_lookup)
    if len(matches) == 1:
        return json.load(open(matches[0], 'r'))
    else:
        raise Exception('metadata file not found, expecting %s' % (metadata_file_lookup,))


def get_item_metadata_from_url(item_id):
    url = '%s/django/workflow/item/%s/json/' % (drlrepo.ingest.config.LEGACY_WORKFLOW_URL, item_id,)
    try:
        return json.loads(urllib2.urlopen(url).read())
    except:
        return None

def get_item_id(m):
    return m['item']['do_id']

def get_item_type(m):
    return m['item']['type']

def get_fedora_collections(m):
    c = []
    for i in m['fedora_collections']:
        c.append(m['fedora_collections'][i]['pid'])
    return c

def get_fedora_sites(m):
    c = []
    for i in m['fedora_sites']:
        c.append(m['fedora_sites'][i]['pid'])
    return c

def get_item_thumbnail_source(m): 
    for f in m['files']:
        if m['files'][f]['name'] == m['item']['thumb_filename']: 
            return m['files'][f]['name']

def get_thumb_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'THUMB':
            return m['files'][f]['name']

def get_thumb_large_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'THUMB_LARGE':
            return m['files'][f]['name']

def get_mods_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'MODS':
            return m['files'][f]['name']

def get_marcxml_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'MARCXML':
            return m['files'][f]['name']

def get_mets_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'METS':
            return m['files'][f]['name']

def get_dc_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'DC':
            return m['files'][f]['name']

def get_master_file_list(m):
    masters = []
    for f in m['files']:
        if m['files'][f]['use'] == 'MASTER':
            masters.append(m['files'][f]['name'])
    return masters 

def get_jp2_file_list(m):
    jp2s = []
    for f in m['files']:
        if m['files'][f]['use'] == 'JP2':
            jp2s.append(m['files'][f]['path'])
    return jp2s 

def get_jp2_name(m, t):
    expected_jp2_name = '%s.%s' % (os.path.splitext(t)[0], 'jp2') 
    for f in m['files']:
        if m['files'][f]['use'] == 'JP2':
            if m['files'][f]['name'] == expected_jp2_name:
                return m['files'][f]['name']
    return None

def get_page_thumb_name(m, t):
    expected_page_thumb_name_jpg = '%s.%s' % (os.path.splitext(t)[0], 'thumb.jpg') 
    expected_page_thumb_name_png = '%s.%s' % (os.path.splitext(t)[0], 'thumb.png') 
    for f in m['files']:
        if m['files'][f]['use'] == 'PAGE_THUMB':
            if m['files'][f]['name'] == expected_page_thumb_name_jpg:
                return m['files'][f]['name']
            elif m['files'][f]['name'] == expected_page_thumb_name_png:
                return m['files'][f]['name']
    return None

def get_ocr_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'OCR_ZIP':
            return m['files'][f]['name']

def get_target_name(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'TARGET':
            return m['files'][f]['name']

