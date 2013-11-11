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
        print '%s purged' % (o.pid,)

if __name__ == '__main__':
    item_id = sys.argv[1]
    print 'purging objects with pids containing %s' % (item_id,)
    purge_item(item_id)
    
