import datetime
import math


class Score(object):
  def __init__(self, crimes):
    self.crimes = crimes

  def generate_score(self):
    return sum([self.generate_individual_score(c) for c in self.crimes])

  def generate_individual_score(self, crime, date_dampening = True):
    exponent = (8 - (int(crime.code) / 100)) * 2
    score = float(2**exponent)
    score = score / (float(crime.distance) + 1)
    if date_dampening:
      days = (datetime.datetime.now() - crime.dispatch_time).days
      return score / math.log(math.e + days)
    else:
      return score

  def generate_partitioned_score(self, date_dampening = True):
    violent = 0
    nonviolent = 0

    for crime in self.crimes:
      if int(crime.code) > 400:
        nonviolent += self.generate_individual_score(crime, date_dampening)
      else:
        violent += self.generate_individual_score(crime, date_dampening)

    return (violent, nonviolent)
