import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
import logging
from eulfedora.server import Repository
from eulxml.xmlmap.dc import DublinCore
from eulxml.xmlmap.mods import MODS 
import eulxml.xmlmap
import drlrepo.repo.models 

repo = Repository()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def add_datastream(pid, this_type, ds_id, content, mimetype):
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
        
if __name__ == '__main__':
    pid = sys.argv[1]
    this_type = sys.argv[2]
    ds_id = sys.argv[3]
    content = sys.argv[4]
    mimetype = None
    if len(sys.argv) > 5:
        mimetype = sys.argv[5]
    add_datastream(pid, this_type, ds_id, content, mimetype)
    logging.info('%s - added datastream OK', pid)
