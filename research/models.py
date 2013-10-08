#!/usr/bin/env python
from peewee import *

import config


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


if __name__ == '__main__':
  Crime.create_table()
