#!/usr/bin/env python
from api.crime.score import Score

DEFAULT_RADIUS = 200  # meters

class Model(object):
  def __init__(self, lat, lon):
    self.crimes = None
    self.radius = DEFAULT_RADIUS
    self.database = None
    self.lat = lat
    self.lon = lon

  def generate_crime_score(self):
    score = Score(self.get_crimes()) 
    return score.generate_score()

  def generate_partitioned_score(self):
    score = Score(self.get_crimes())
    return score.generate_partitioned_score()

  def get_simple_count(self):
    return len(self.get_crimes(self.radius))

  def get_recent(self, count=5):
    crimes = sorted(self.get_crimes(),
      key = lambda c: c.dispatch_time)
    crimes.reverse()
    
    return crimes[0:count]

  def generate_monthly_score(self):
    groups = {}
    for crime in self.get_crimes():
      key = crime.dispatch_time.strftime('%Y-%m')
      if key not in groups:
        groups[key] = []
      groups[key].append(crime)

    results = {}
    for key, crimes in groups.items():
      score = Score(crimes)
      (violent, nonviolent) = score.generate_partitioned_score(False)
      results[key] = {
        'violent': violent,
        'nonviolent': nonviolent
      }

    return results
  
  def _set_database(self, database):
    self.database = database

  def _get_database(self):
    if self.database is None:
      from api.crime.database import Database
      self.database = Database()
    return self.database

  def get_crimes(self, meters = DEFAULT_RADIUS, force = False):
    if self.crimes is None or force or self.radius != meters:
      self.radius = meters
      db = self._get_database()
      self.crimes = db.load_crimes(self.lat, self.lon, meters)
    return self.crimes
