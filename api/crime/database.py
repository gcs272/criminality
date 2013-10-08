#!/usr/bin/env python
from peewee import *
from peewee import RawQuery
import json

from api import config


db = PostgresqlDatabase(config.DATABASE_NAME, 
  user = config.DATABASE_USER,
  password = config.DATABASE_PASS,
  host = config.DATABASE_HOST)

class BaseModel(Model):
  class Meta:
    database = db

class Crime(BaseModel):
  district      = CharField(null = False, max_length=2)
  sector        = CharField(null = False, max_length=1)
  dispatch_time = DateTimeField(null = False)
  location      = CharField(null = False)
  description   = CharField(null = False)
  code          = CharField(null = False, max_length=6)
  lat           = DecimalField(null = False)
  lon           = DecimalField(null = False)
  distance      = DecimalField()

  def dict(self):
    return {
      'district': self.district,
      'dispatch_time': self.dispatch_time.isoformat(),
      'location': self.location,
      'description': self.description,
      'code': self.code,
      'lat': float(self.lat),
      'lon': float(self.lon),
      'distance': float(self.distance)
    }

class Database(object):
  def load_crimes(self, lat, lon, meters):
    return [c for c in RawQuery(Crime, """
      SELECT *, ST_Distance_Sphere(geom, ST_GeomFromText('POINT(%0.6f %0.6f)', 4326)) AS distance
      FROM crime
      WHERE ST_Distance_Sphere(geom, ST_GeomFromText('POINT(%0.6f %0.6f)', 4326)) < %d
      """ % (lon, lat, lon, lat, meters)).execute()]


if __name__ == '__main__':
  Crime.create_table()
