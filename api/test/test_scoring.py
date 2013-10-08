import datetime
import unittest

from api.crime.score import Score
from api.crime.database import Crime


class ScoringTest(unittest.TestCase):
  def test_date_log(self):
    """ Crimes shouldn't have a linear roll off with date, it should probably
      be a log of the number of days (plus e: log(e) == 1) """
    score = Score([])

    now = datetime.datetime.now()
    crime = Crime(code = 100, dispatch_time = now, distance = 10)
    now_score = score.generate_individual_score(crime)

    crime = Crime(code = 100, dispatch_time = now - datetime.timedelta(7),
      distance = 10)
    last_week_score = score.generate_individual_score(crime)

    crime = Crime(code = 100, dispatch_time = now - datetime.timedelta(30),
      distance = 10)
    last_month_score = score.generate_individual_score(crime)

    crime = Crime(code = 100, dispatch_time = now - datetime.timedelta(365),
      distance = 10)
    last_year_score = score.generate_individual_score(crime)

    self.assertTrue(now_score / 2 > last_week_score)
    self.assertTrue(now_score / 3 < last_week_score)

    self.assertTrue(now_score / 3 > last_month_score)
    self.assertTrue(now_score / 4 < last_month_score)

    self.assertTrue(now_score / 5 > last_year_score)
    self.assertTrue(now_score / 6 < last_year_score)

  def test_ignoring_date(self):
    score = Score([])
    now = datetime.datetime.now()

    c1 = Crime(code = 100, dispatch_time = now, distance = 10)
    c2 = Crime(code = 100, dispatch_time = now - datetime.timedelta(365), 
      distance = 10)

    s1 = score.generate_individual_score(c1, False)
    s2 = score.generate_individual_score(c2, False)

    self.assertEqual(s1, s2)
    
  def test_distance_scoring(self):
    score = Score([])
    now = datetime.datetime.now()
    c1 = Crime(code = 100, dispatch_time = now, distance = 100)
    c2 = Crime(code = 100, dispatch_time = now, distance = 10)

    self.assertTrue(score.generate_individual_score(c1)  <
      score.generate_individual_score(c2))

  def test_serious_crime_scoring(self):
    """ Murders should be *way* worse than petty theft """
    score = Score([])
    now = datetime.datetime.now()
    c1 = Crime(code = 100, dispatch_time = now, distance = 10)
    c2 = Crime(code = 600, dispatch_time = now, distance = 10)

    s1 = score.generate_individual_score(c1)
    s2 = score.generate_individual_score(c2)

    self.assertTrue(s1 > s2 * 100)

  def test_score_partitioning(self):
    """ Be able to split the score into violent/non-violent """
    now = datetime.datetime.now()

    c1 = Crime(code=100, dispatch_time = now, distance = 10)
    c2 = Crime(code=500, dispatch_time = now, distance = 10)

    score = Score([c1, c2])
    (violent, nonviolent) = score.generate_partitioned_score()
    combined = score.generate_score()

    self.assertTrue(violent > nonviolent)
    self.assertEquals(combined, violent + nonviolent)

