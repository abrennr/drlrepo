import sys
import os
import zipfile
import subprocess
import shutil
import glob
import json
import drlutils.image.utils
import drlrepo.ingest.config
from drlrepo.repo.models import PittLargeImage, PittBook, PittPage, PittNewspaperIssue 
"""
Utility script to migrate digital objects from the legacy (as of 2012)
DRL repository to Fedora.

For each object, determine content
type and route to a handler function that will create the object in 
Fedora and upload all relevant datastreams.
"""


# map of legacy item types to eulfedora digital object models 
ITEM_TYPE_CM_MAP = {
    'image': PittLargeImage,
    'text - cataloged': PittBook,
    'text - uncataloged': PittBook,
    'newspaper - cataloged': PittNewspaperIssue,
    'newspaper - uncataloged': PittNewspaperIssue,
    'map': PittLargeImage,
    'manuscript': PittBook,
    'page': PittPage
}

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

def get_item_thumbnail_source(m): 
    for f in m['files']:
        if m['files'][f]['name'] == m['item']['thumb_filename']: 
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
    expected_jp2_name = t.replace('.tif', '.jp2') 
    for f in m['files']:
        if m['files'][f]['use'] == 'JP2':
            if m['files'][f]['name'] == expected_jp2_name:
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

def create_thumbnail(thumb_source):
    """
    Creates a larger thumbnail (i.e., 250px on the long side) than what exists
    in the legacy repository.  

    @param item_id: object identifier 
    @param thumb_source: if provided, use to create thumbnail, else look up 

    returns path to the thumbnail file

    """
    shutil.copy(thumb_source, drlrepo.ingest.config.TEMP_DIR)
    thumb_temp = os.path.join(drlrepo.ingest.config.TEMP_DIR, os.path.basename(thumb_source))
    thumb_file = drlutils.image.utils.encode_thumb(thumb_temp, clobber=True, size='250') 
    os.remove(thumb_temp)
    return thumb_file

def create_tmp_jp2(parent, tiff):
    shutil.copy(tiff, drlrepo.ingest.config.TEMP_DIR)
    jp2_source = os.path.join(drlrepo.ingest.config.TEMP_DIR, os.path.basename(tiff))
    type = 'image'
    if 'text' in parent.type: 
        type = 'text'
    jp2_file = drlutils.image.utils.encode_jp2(jp2_source, clobber=True, type=type) 
    os.remove(jp2_source)
    return jp2_file


"""
Note: this converter is not finished yet
"""
def create_pdf(fedora_object, tiff):
    """
    Create pdf derivative from tiff
    """
    baseName = os.path.splitext(tiff.name)[0]
    pdf_file = os.path.join("drlrepo.ingest.config.TEMP_DIR", "%s.pdf" % baseName)
    #os.remove(pdf_file)
    return

