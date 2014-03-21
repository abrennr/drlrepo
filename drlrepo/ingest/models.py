import sys
import os
import zipfile
import shutil
import drlrepo.ingest.utils
import drlrepo.ingest.config
import drlutils.mods.utils
import drlutils.mets.utils
import logging

"""
Models to hold relevant metadata (e.g., file paths, datastream names)
for objects being ingested into Fedora.

The BaseIngestObject is initialized with a path to a bagit bag containing
object files and metadata.  The administrative metadata is parsed and
the relevant datastream paths and names are set.

If the object is multi-paged, each page becomes a separate PageIngestObject
which will be ingested separately by the main ingest process.
"""
class CollectionIngestObject:
    """A representation of a collection object to be ingested."""

    def __init__(self, bag_path):
        self.item_id = os.bath.basename(bag_path)
        pathroot = os.path.join(bag_path, 'data')
        thumb_filename = '%s.thumb.jpg' % (self.item_id,)
        self.thumb_path = os.path.join(pathroot, thumb_filename)
        large_thumb_filename = '%s.thumb_large.jpg' % (self.item_id,)
        self.large_thumb_path = os.path.join(pathroot, large_thumb_filename)
        description_filename = '%s.description.html' % (self.item_id,) 
        self.description_path = os.path.join(pathroot, description_filename)

    def is_valid(self):
        valid = True
        for path in [self.thumb_path, self.large_thumb_path, self.description_path]:
            if not os.path.exists(path):
                valid = False
                logging.error('%s - %s does not exist' % (self.item_id, path))
        return valid
            

class BaseIngestObject:
    """A representation of a local object to be ingested."""
    pages = []
    # optional fields:
    target_label = None 
    fits_path = None

    def __init__(self, bag_path):
        pathroot = os.path.join(bag_path, 'data')
        m = drlrepo.ingest.utils.get_item_metadata(bag_path)
        self.item_id = drlrepo.ingest.utils.get_item_id(m)
        self.pid = 'pitt:%s' % (self.item_id,)
        self.type = drlrepo.ingest.utils.get_item_type(m)
        self.fedora_type = drlrepo.ingest.utils.ITEM_TYPE_CM_MAP[self.type]
        self.mods_label = drlrepo.ingest.utils.get_mods_name(m)
        self.mods_path = os.path.join(pathroot, self.mods_label)
        parsed_mods = drlutils.mods.utils.get_parsed_mods(self.mods_path)
        self.label = unicode(drlutils.mods.utils.get_title(parsed_mods)) 
        self.dc_label = drlrepo.ingest.utils.get_dc_name(m)
        self.dc_path = os.path.join(pathroot, self.dc_label) 
        self.marcxml_label = drlrepo.ingest.utils.get_marcxml_name(m)
        if self.marcxml_label:
            self.marcxml_path = os.path.join(pathroot, self.marcxml_label) 
        self.mets_label = drlrepo.ingest.utils.get_mets_name(m)
        if self.mets_label:
            self.mets_path = os.path.join(pathroot, self.mets_label) 
        self.target_label = drlrepo.ingest.utils.get_target_name(m)
        if self.target_label:
            self.target_path = os.path.join(pathroot, self.target_label) 
        self.thumbnail_large_label = drlrepo.ingest.utils.get_thumb_large_name(m)
        self.thumbnail_large_path = os.path.join(pathroot, self.thumbnail_large_label) 
        self.thumbnail_label = drlrepo.ingest.utils.get_thumb_name(m)
        self.thumbnail_path = os.path.join(pathroot, self.thumbnail_label)
        self.fedora_collections = drlrepo.ingest.utils.get_fedora_collections(m)
        self.fedora_sites = drlrepo.ingest.utils.get_fedora_sites(m)
        master_files = drlrepo.ingest.utils.get_master_file_list(m)
        if len(master_files) > 1:
            # assume this is a paged object
            parsed_mets = drlutils.mets.utils.get_parsed_mets(self.mets_path)
            page_label_dict = drlutils.mets.utils.get_page_label_dict(parsed_mets)
            cleaned_page_labels = drlutils.mets.utils.clean_page_labels(page_label_dict)
            ocr_file = drlrepo.ingest.utils.get_ocr_name(m)
            # ocr is not always present:
            if ocr_file:
                ocr_path = os.path.join(pathroot, ocr_file)
                ocr_zip = zipfile.ZipFile(ocr_path, 'r')
            for f in master_files:
                label = cleaned_page_labels[f]
                logging.debug('preparing page %s', label)
                f_path = os.path.join(pathroot, f) 
                page = PageIngestObject(self, f_path, label, m)
                if ocr_file:
                    ocr_label = '%s.txt' % (os.path.splitext(f)[0],)
                    if ocr_label in ocr_zip.namelist():
                        ocr_zip.extract(ocr_label, drlrepo.ingest.config.TEMP_DIR) 
                        page.ocr_label = ocr_label
                        page.ocr_path = os.path.join(drlrepo.ingest.config.TEMP_DIR, ocr_label) 
                self.pages.append(page)
        elif len(master_files) == 1:
            # handle image-type object
            self.obj_label = unicode(master_files[0])
            self.obj_path = os.path.join(pathroot, self.obj_label) 
            fits_path = '%s.fits.xml' % (self.obj_path,) 
            if os.path.exists(fits_path):
                self.fits_path = fits_path
                self.fits_label = os.path.basename(fits_path)
            self.jp2_label = drlrepo.ingest.utils.get_jp2_name(m, self.obj_label)
            self.jp2_path = os.path.join(pathroot, self.jp2_label)
        else:
            # no master images?
            pass

    def remove_thumbnail(self):
        try:
            os.remove(self.thumbnail_path)
        except:
            pass

class PageIngestObject:
    """A representation of a page object. Child of a parent object being ingested."""
    fedora_type = drlrepo.ingest.utils.ITEM_TYPE_CM_MAP['page']
    # optional fields:
    ocr_path = None
    fits_path = None

    def __init__(self, parent, obj_path, label, m):
        pathroot = os.path.split(obj_path)[0]
        page_basename = os.path.splitext(os.path.basename(obj_path))[0]
        self.seq = str(int(page_basename))
        self.pid = '%s-%s' % (parent.pid, page_basename)
        self.label = u'%s, %s' % (label, parent.label[0:205])
        self.obj_path = obj_path 
        self.obj_label = unicode(os.path.basename(self.obj_path))
        fits_path = '%s.fits.xml' % (self.obj_path,) 
        if os.path.exists(fits_path):
            self.fits_path = fits_path
            self.fits_label = os.path.basename(fits_path)
        self.jp2_label = drlrepo.ingest.utils.get_jp2_name(m, self.obj_label)
        self.jp2_path = os.path.join(pathroot, self.jp2_label) 
        self.thumbnail_label = drlrepo.ingest.utils.get_page_thumb_name(m, self.obj_label)
        self.thumbnail_path = os.path.join(pathroot, self.thumbnail_label) 
        self.ocr_path = None
        self.ocr_label = None

    def remove_ocr(self):
        try:
            os.remove(self.ocr_path)
        except:
            pass

    def remove_thumbnail(self):
        try:
            os.remove(self.thumbnail_path)
        except:
            pass

