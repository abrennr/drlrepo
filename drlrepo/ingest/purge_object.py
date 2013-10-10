import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'drlrepo.settings'
from eulfedora.server import Repository

def purge_item(item_id):
    repo = Repository()
    pid = 'pitt:%s' % (item_id,)
    objs = repo.find_objects(pid__contains=pid)
    for o in objs:
        repo.purge_object(o.pid)

if __name__ == '__main__':
    item_id = sys.argv[1]
    print 'working with %s' % (item_id,)
    purge_item(item_id)
    print '%s purged' % (item_id,)
    
