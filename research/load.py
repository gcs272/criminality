#!/usr/bin/env python
import csv
import sys

from models import Crime
from models import db


def load(fp):
  reader = csv.reader(fp)
  reader.next() # Throw out the column headers

  with db.transaction():
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

  db.execute_sql("""
    UPDATE crime SET geom = ST_GeomFromText(
      'POINT(' || lon || ' ' || lat || ')', 4326
    );""")

if __name__ == '__main__':
  """ Crime data from http://www.opendataphilly.org/opendata/resource/215/philadelphia-police-part-one-crime-incidents/ """
  if len(sys.argv) < 2:
    import StringIO
    import requests
    import zipfile
    
    resp = requests.get('http://gis.phila.gov/data/police_inct.zip')
    zf = StringIO.StringIO(resp.content)
    load(zipfile.ZipFile(zf).open('police_inct.csv'))
  else:
    load(open(sys.argv[1]))
