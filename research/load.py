#!/usr/bin/env python
import csv
import sys
import progressbar

from models import Crime
from models import db


def load(filename):
  lines = 0
  for line in open(filename):
    lines += 1

  with open(filename) as fp:
    reader = csv.reader(fp)
    reader.next() # Throw out the column headers

    progress = progressbar.ProgressBar(maxval = lines)
    progress.start()

    with db.transaction():
      read = 0
      for row in reader:
        crime = Crime(
          district = row[0],
          sector = row[1],
          dispatch_time = row[2],
          location = row[7],
          code = row[8],
          description = row[10],
          lon = row[12],
          lat = row[13])
        crime.save(force_insert = True)
        
        read += 1
        progress.update(read)

    db.execute_sql("""
      UPDATE crime SET geom = ST_GeomFromText(
        'POINT(' || lon || ' ' || lat || ')', 4326
      );""")

if __name__ == '__main__':
  """ Crime data from http://www.opendataphilly.org/opendata/resource/215/philadelphia-police-part-one-crime-incidents/ """
  if len(sys.argv) < 2:
    print 'usage: python load.py /path/to/police_inct.csv'
    sys.exit(0)

  load(sys.argv[1])
