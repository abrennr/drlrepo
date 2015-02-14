import sys
import csv
from drlrepo.ingest.utils import add_datastream

def main(csv_file):
    my_csv = csv.reader(open(csv_file))
    for row in my_csv:
        (pid, f_type, ds_label, content_path) = row[0:4]
        if len(row) > 4:
            mimetype = row[4]
        else:
            mimetype = None
        try:
            add_datastream(pid, f_type, ds_label, content_path, mimetype)
        except:
            pass


if __name__ == '__main__':
    main(sys.argv[1])
