#!/usr/bin/env python
import datetime
import mock
import unittest

from api.crime.model import Model
from api.crime.database import Crime


class BasicModelTest(unittest.TestCase):
  def setUp(self):
    self.db = mock.Mock()
    self.db.load_crimes.return_value = 1234

    self.model = Model(1, 2)
    self.model._set_database(self.db)

  def test_data_loading(self):
    self.model.get_crimes(100)

    self.assertEquals(1, self.db.load_crimes.call_count)

    self.model.get_crimes(100)
    self.assertEquals(1, self.db.load_crimes.call_count)

    # Change the radius
    self.model.get_crimes(50)
    self.assertEquals(2, self.db.load_crimes.call_count)

    # Check the radius
    self.model.get_crimes(50)
    self.assertEquals(2, self.db.load_crimes.call_count)

    # Check forcing
    self.model.get_crimes(50, force = True)
    self.assertEquals(3, self.db.load_crimes.call_count)

  def test_simple_counting_model(self):
    self.db.load_crimes.return_value = [Crime(), Crime(), Crime()]
    
    count = self.model.get_simple_count()
    
    self.db.load_crimes.assert_called_with(1, 2, 200)
    self.assertEquals(3, count)
    
  def test_get_latest(self):
    now = datetime.datetime.now()
    self.db.load_crimes.return_value = [
      Crime(dispatch_time = now - datetime.timedelta(3600), description = 'b',
        distance = 10),
      Crime(dispatch_time = now, description='a', distance = 10),
      Crime(dispatch_time = now - datetime.timedelta(36000),
        description = 'd', distance = 10),
      Crime(dispatch_time = now - datetime.timedelta(18000),
        description = 'c', distance = 10)
    ]

    crimes = self.model.get_recent(3)
    self.assertEquals(3, len(crimes))
    self.assertEquals('a', crimes[0].description)
    self.assertEquals('b', crimes[1].description)
    self.assertEquals('c', crimes[2].description)

  def test_type_sanity(self):
    """ Test that murders > gunshots > thefts, all other things equal """

    now = datetime.datetime.now()
    self.db.load_crimes.return_value = [
      Crime(code = 100, description = 'Homicide - Criminal',
        dispatch_time = now, distance = 10),
    ]

    murder_score = self.model.generate_crime_score()

    self.db.load_crimes.return_value = [
      Crime(code = 400, description = 'Aggravated Assault Firearm',
        dispatch_time = now, distance = 10)
    ]

    self.model = Model(1,0)
    self.model._set_database(self.db)
    gunshot_score = self.model.generate_crime_score()

    self.db.load_crimes.return_value = [
      Crime(code = 600, description = 'Thefts',
        dispatch_time = now, distance = 10)
    ]

    self.model = Model(1,0)
    self.model._set_database(self.db)
    theft_score = self.model.generate_crime_score()

    self.assertTrue(murder_score > gunshot_score)
    self.assertTrue(gunshot_score > theft_score)

  def test_recency_sanity(self):
    """ Make sure that more recent crimes count for more """

    self.db.load_crimes.return_value = [
      Crime(code = 100, dispatch_time = datetime.datetime.now(),
        distance = 10)
    ]

    holyshit_score = self.model.generate_crime_score()

    self.db.load_crimes.return_value = [
      Crime(code = 100, dispatch_time = datetime.datetime.now() -
        datetime.timedelta(1), distance = 10)
    ]

    self.model = Model(1,0)
    self.model._set_database(self.db)
    
    yesterday_score = self.model.generate_crime_score()

    self.assertTrue(holyshit_score > yesterday_score)
  
  def test_date_bucket_scoring(self):
    base = datetime.datetime.strptime('2013-04-01', '%Y-%m-%d')

    c1 = Crime(code=100, dispatch_time = base, distance = 10)
    c2 = Crime(code=200, dispatch_time = base - datetime.timedelta(20),
      distance = 10)
    c3 = Crime(code=100, dispatch_time = base - datetime.timedelta(40),
      distance = 10)

    model = Model(1, 0)
    model.crimes = [c1, c2, c3]
    results = model.generate_monthly_score()
    
    self.assertTrue('2013-04' in results)
    self.assertTrue('2013-02' in results)
    self.assertTrue('nonviolent' in results['2013-04'])
    self.assertEquals(results['2013-04']['violent'],
      results['2013-02']['violent'])
    self.assertTrue(results['2013-04']['violent'] >
      results['2013-03']['violent'])
