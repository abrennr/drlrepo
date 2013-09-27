import sys
import os
import zipfile
import shutil
import utils as ingest_utils
sys.path.append('/usr/local/dlxs/prep/w/workflow/lib')
import drl.mods.utils
import drl.mets.utils

class BaseIngestObject:
    item_id = None
    pid = None 
    type = None 
    label = None
    fedora_type = None 
    mods_path = None 
    mods_label = None 
    dc_path = None 
    dc_label = None 
    obj_path = None 
    obj_label = None 
    jp2_path = None 
    jp2_label = None 
    jp2_is_temp = False
    pages = []
    mets_path = None
    mets_label = None 
    marcxml_path = None
    marcxml_label = None 
    thumbnail_path = None 
    thumbnail_label = None 

    def __init__(self, item_id):
        self.item_id = item_id
        self.pid = 'pitt:%s' % (item_id,)
        print 'getting metadata'
        m = ingest_utils.get_item_metadata(self.item_id)
        self.type = ingest_utils.get_item_type(m)
        self.fedora_type = ingest_utils.ITEM_TYPE_CM_MAP[self.type]
        print 'mods'
        self.mods_path = ingest_utils.get_mods_path(m)
        self.mods_label = unicode(os.path.basename(self.mods_path))
        parsed_mods = drl.mods.utils.get_parsed_mods(self.mods_path)
        self.label = unicode(drl.mods.utils.get_title(parsed_mods)) 
        print 'dc'
        self.dc_path = ingest_utils.get_dc_path(m)
        self.dc_label = unicode(os.path.basename(self.dc_path))
        self.marcxml_path = ingest_utils.get_marcxml_path(m)
        if self.marcxml_path:
            self.marxml_label = unicode(os.path.basename(self.marcxml_path))
        self.mets_path = ingest_utils.get_mets_path(m)
        if self.mets_path:
            self.mets_label = unicode(os.path.basename(self.mets_path))
        print 'thumbnail'
        item_thumbnail_source = ingest_utils.get_item_thumbnail_source(m)
        self.thumbnail_path = ingest_utils.create_thumbnail(item_thumbnail_source)
        self.thumbnail_label = unicode(os.path.basename(self.thumbnail_path))
        master_files = ingest_utils.get_master_file_list(m)
        if len(master_files) > 1:
            print 'has pages'
            parsed_mets = drl.mets.utils.get_parsed_mets(self.mets_path)
            page_label_dict = drl.mets.utils.get_page_label_dict(parsed_mets)
            cleaned_page_labels = drl.mets.utils.clean_page_labels(page_label_dict)
            ocr_path = ingest_utils.get_ocr_path(m)
            ocr_zip = zipfile.ZipFile(ocr_path, 'r')
            for f in master_files:
                label = cleaned_page_labels[os.path.basename(f)]
                print 'page %s' % (label,)
                page = PageIngestObject(self, f, label, m)
                ocr_label = '%s.txt' % (os.path.splitext(os.path.basename(f))[0],)
                if ocr_label in ocr_zip.namelist():
                    ocr_zip.extract(ocr_label, '/usr/local/tmp') 
                    page.ocr_label = ocr_label
                    page.ocr_path = os.path.join('/usr/local/tmp', ocr_label) 
                self.pages.append(page)
        elif len(master_files) == 1:
            # handle image-type object
            self.obj_path = master_files[0] 
            self.obj_label = unicode(os.path.basename(self.obj_path))
            self.jp2_path = ingest_utils.get_jp2_path(m, self.obj_path)
            if not self.jp2_path:
                self.jp2_path = ingest_utils.create_tmp_jp2(self, self.obj_path)
                self.jp2_is_temp = True
            self.jp2_label = unicode(os.path.basename(self.jp2_path))
            pass

    def remove_thumbnail(self):
        try:
            os.remove(self.thumbnail_path)
        except:
            pass

    def remove_jp2(self):
        os.remove(self.jp2_path)

class PageIngestObject:
    fedora_type = ingest_utils.ITEM_TYPE_CM_MAP['page']
    pid = None 
    label = None 
    seq = None
    obj_path = None
    obj_label = None
    jp2_path = None
    jp2_label = None
    jp2_is_temp = False
    thumbnail_path = None
    thumbnail_label = None
    ocr_path = None
    ocr_label = None

    def __init__(self, parent, obj_path, label, m):
        page_basename = os.path.splitext(os.path.basename(obj_path))[0]
        self.seq = str(int(page_basename))
        self.pid = '%s-%s' % (parent.pid, page_basename)
        self.label = u'%s, %s' % (label, parent.label[0:205])
        self.obj_path = obj_path 
        self.obj_label = unicode(os.path.basename(self.obj_path))
        print 'page %s jp2' % (label,)
        self.jp2_path = ingest_utils.get_jp2_path(m, self.obj_path)
        if not self.jp2_path:
            self.jp2_path = ingest_utils.create_tmp_jp2(parent, self.obj_path)
            self.jp2_is_temp = True
        self.jp2_label = unicode(os.path.basename(self.jp2_path))
        print 'page %s thumb' % (label,)
        self.thumbnail_path = ingest_utils.create_thumbnail(self.obj_path)
        self.thumbnail_label = unicode(os.path.basename(self.thumbnail_path))

    def remove_ocr(self):
        os.remove(self.ocr_path)

    def remove_thumbnail(self):
        try:
            os.remove(self.thumbnail_path)
        except:
            pass

    def remove_jp2(self):
        os.remove(self.jp2_path)

