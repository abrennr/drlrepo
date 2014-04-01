import sys
import os
import zipfile
import subprocess
import shutil
import glob
import json
import drlutils.image.utils
import drlrepo.ingest.config
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

def get_jp2_name(m, t):
    expected_jp2_name = '%s.%s' % (os.path.splitext(t)[0], 'jp2') 
    for f in m['files']:
        if m['files'][f]['use'] == 'JP2':
            if m['files'][f]['name'] == expected_jp2_name:
                return m['files'][f]['name']
    return None

def get_page_thumb_name(m, t):
    expected_page_thumb_name = '%s.%s' % (os.path.splitext(t)[0], 'thumb.jpg') 
    for f in m['files']:
        if m['files'][f]['use'] == 'PAGE_THUMB':
            if m['files'][f]['name'] == expected_page_thumb_name:
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

