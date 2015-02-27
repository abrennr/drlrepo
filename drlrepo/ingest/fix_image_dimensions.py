import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
from eulfedora.server import Repository
import eulxml.xmlmap
from drlrepo.repo.models import PittPage
import drlrepo.ingest.utils
import drlrepo.ingest.config
import logging
import logging.config
import requests
from rdflib import RDFS, Literal, Namespace

repo = Repository()
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('fixLogger')

def fix_page_object(page_pid, page_jp2_path, fedora_sites):
    """
    The page object gets some extra relationships as a member of a book object.
    """
    page_obj = repo.get_object(pid=page_pid, type=PittPage)
    logger.debug('retrieved page object %s', page_obj.uriref)

    # TODO: Remove existing RELS-INT
    api_call_url = 'http://da-fed.library.pitt.edu:8080/fedora/objects/%s/datastreams/RELS-INT' % (page_pid,)
    logger.debug('REST-API call: %s', api_call_url)
    r = requests.delete(api_call_url, auth=(drlrepo.ingest.config.FEDORA_USER, drlrepo.ingest.config.FEDORA_PASS))
    if not r.status_code == requests.codes.ok:
        logger.warning('problem removing existing RELS-INT: %s - %s', r.status_code, r.text)
        return 1
    logger.debug('REST-API call returned OK')

    # RELS-INT
    # include height and width of JP2 datastream
    [this_width, this_height] = drlrepo.ingest.utils.get_image_dimensions(page_jp2_path) 
    jp2_uri = page_obj.uriref + u'/JP2'
    ISLANDORA_NS = Namespace(u'http://islandora.ca/ontology/relsext#')
    ISLANDORA_NS.width
    ISLANDORA_NS.height
    page_obj.rels_int.content.add((jp2_uri, ISLANDORA_NS.width, Literal(this_width)))
    page_obj.rels_int.content.add((jp2_uri, ISLANDORA_NS.height, Literal(this_height)))
    page_obj.save(logMessage="setting RELS-INT info")
   
 
    # add relationships to existing RELS-EXT

    # collection isMemberOf
    for site_pid in fedora_sites:
        isMemberOfSite = 'http://digital.library.pitt.edu/ontology/relations#isMemberOfSite'
        parent_uri = "info:fedora/%s" % (site_pid,)
        page_obj.add_relationship(isMemberOfSite, str(parent_uri))

    logger.info('fixed %s', page_pid)


if __name__ == '__main__':
    do_id = sys.argv[1]
    logger.debug('working with %s', do_id)
    m = drlrepo.ingest.utils.get_item_metadata_from_url(do_id)
    fedora_sites = drlrepo.ingest.utils.get_fedora_sites(m)
    jp2_file_list = drlrepo.ingest.utils.get_jp2_file_list(m)
    if len(jp2_file_list) == 0:
        logger.warning('no jp2 files found for %s', do_id)
    else:
        for jp2_path in jp2_file_list:
            page_seq = os.path.splitext(os.path.basename(jp2_path))[0] 
            page_pid = 'pitt:' + do_id + '-' + page_seq
            logger.debug('calling fix_page_object with %s, %s', page_pid, jp2_path)
            error_status = fix_page_object(page_pid, jp2_path, fedora_sites)           
        if error_status:
            logger.warning('%s problems fixing pages', do_id)
        else:
            logger.info('%s pages fixed OK', do_id)
