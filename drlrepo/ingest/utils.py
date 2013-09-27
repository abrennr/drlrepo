import sys
import os
import zipfile
import subprocess
import shutil
import urllib2
import json
sys.path.append('/home/abrenner/django/drlrepo')
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

def get_item_metadata(item_id):
    url = 'http://bigfoot.library.pitt.edu/django/workflow/item/%s/json/' % (item_id,)
    u = urllib2.urlopen(url)
    return json.load(u)

def get_item_type(m):
    return m['item']['type']

def get_item_thumbnail_source(m): 
    for f in m['files']:
        if m['files'][f]['name'] == m['item']['thumb_filename']: 
            return m['files'][f]['path']

def get_mods_path(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'MODS':
            return m['files'][f]['path']

def get_marcxml_path(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'MARCXML':
            return m['files'][f]['path']

def get_mets_path(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'METS':
            return m['files'][f]['path']

def get_dc_path(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'DC':
            return m['files'][f]['path']

def get_master_file_list(m):
    masters = []
    for f in m['files']:
        if m['files'][f]['use'] == 'MASTER':
            masters.append(m['files'][f]['path'])
    return masters 

def get_jp2_path(m, t):
    expected_jp2_path = t.replace('.tif', '.jp2') 
    for f in m['files']:
        if m['files'][f]['use'] == 'JP2':
            if m['files'][f]['path'] == expected_jp2_path:
                return m['files'][f]['path']
    return None

def get_ocr_path(m):
    for f in m['files']:
        if m['files'][f]['use'] == 'OCR_ZIP':
            return m['files'][f]['path']

def create_thumbnail(thumb_source):
    """
    Creates a larger thumbnail (i.e., 250px on the long side) than what exists
    in the legacy repository.  

    @param item_id: object identifier 
    @param thumb_source: if provided, use to create thumbnail, else look up 

    returns path to the thumbnail file

    """
    shutil.copy(thumb_source, '/usr/local/tmp/')
    thumb_temp = os.path.join('/usr/local/tmp', os.path.basename(thumb_source))
    encoder = '/usr/local/dlxs/prep/w/workflow/bin/image/encodeThumb'
    thumb_file = subprocess.Popen([encoder, thumb_temp, "250"], stdout=subprocess.PIPE).communicate()[0].strip()
    os.remove(thumb_temp)
    return thumb_file

def create_tmp_jp2(parent, tiff):
    shutil.copy(tiff, '/usr/local/tmp/')
    jp2_source = os.path.join('/usr/local/tmp', os.path.basename(tiff))
    if 'text' in parent.type: 
        encoder = '/usr/local/dlxs/prep/w/workflow/bin/image/encodeJp2TextsKdu'
    else:
        encoder = '/usr/local/dlxs/prep/w/workflow/bin/image/encodeJp2Kdu'
    jp2_file = subprocess.Popen(
        [encoder, jp2_source],
        stdout=subprocess.PIPE).communicate()[0].strip()
    os.remove(jp2_source)
    return jp2_file

"""
Note: this converter is not finished yet
"""
def create_mix(tiff):
    """
    Extract MIX metadata from the input tiff file
    """
    basename = os.path.splitext(tiff.name)[0]
    mix_file = os.path.join("/usr/local/tmp", "%s.mix.xml" % baseName)
    out_file = open(mix_file, "w")
    #cmd= jhove -h xml $INFILE | xsltproc jhove2mix.xslt - > `basename ${$INFILE%.*}.mix`
    jhoveCmd1 = ["/opt/jhove/jhove", "-h", "xml", tiff.name]
    jhoveCmd2 = ["xsltproc", "data/jhove2mix.xslt", "-"] # complete cmd for xsltproc
    #jhoveCmd2 = ["xalan", "-xsl", "data/jhove2mix.xslt"] # complete cmd for xalan
    p1 = subprocess.Popen(jhoveCmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(jhoveCmd2, stdin=p1.stdout, stdout=out_file)
    r = p2.communicate()
    if os.path.getsize(mix_file) == 0:
        # failed for some reason
        print("jhove conversion failed")
    else:
        pass
    out_file.close()
    """ end extract """
    os.remove(mix_file) # finished with that
    return

"""
Note: this converter is not finished yet
"""
def create_pdf(fedora_object, tiff):
    """
    Create pdf derivative from tiff
    /usr/local/dlxs contains an encoder for this?
    """
    baseName = os.path.splitext(tiff.name)[0]
    pdf_file = os.path.join("/usr/local/tmp", "%s.pdf" % baseName)
    #os.remove(pdf_file)
    return

