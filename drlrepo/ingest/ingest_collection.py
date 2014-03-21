import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
import logging
import bagit
import csv
import time
from eulfedora.server import Repository
from drlrepo.repo.models import PittCollection

repo = Repository()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def ingest_collection(pid, label, sites):
    logging.info('working with item %s, label %s, sites %s' % (pid, label, sites))
    # check if item already exists.  For now, purge pre-existing versions
#    previous = repo.get_object(pid=pid)
#    if previous.exists:
#        repo.purge_object(pid)
    obj = repo.get_object(pid=pid, create=True, type=PittCollection)
    obj.label = label
    # dc
    #obj.dc.content = eulxml.xmlmap.load_xmlobject_from_file(o.dc_path, xmlclass=DublinCore)
    #obj.dc.label = o.dc_label 
    # thumb
    #obj.thumbnail.content = open(o.thumbnail_path)
    #obj.thumbnail.label = o.thumbnail_label 
    # large thumb
    #obj.thumbnail_large.content = open(o.thumbnail_large_path)
    #obj.thumbnail_large.label = o.thumbnail_large_label 
    # initial save
    obj.save()
        
    # RELS-EXT
    # collection isMemberOf
    for coll_pid in sites:
        isMemberOf = 'http://digital.library.pitt.edu/ontology/relations#isMemberOfSite'
        parent_uri = 'info:fedora/%s' % (coll_pid,)
        obj.add_relationship(isMemberOf, parent_uri)

if __name__ == '__main__':
    this_csv = csv.reader(open(sys.argv[1], 'r'))
    for line in this_csv:
        pid = line[0]
        label = line[1]
        sites = line[2].strip().split(' ') 
#    pid = sys.argv[1]
#    label = sys.argv[2]
#    sites = sys.argv[3:]
        logging.debug('working with %s, %s, %s', pid, label, sites)
        ingest_collection(pid, label, sites)
        time.sleep(2)
        logging.info('%s ingested OK', pid)
