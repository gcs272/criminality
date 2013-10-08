#!/usr/bin/env python
from flask import Flask, render_template, make_response, request, jsonify
import json

from cors import crossdomain

from api.crime.model import Model


app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/')
@crossdomain(origin='*')
def endpoint():
  if 'lat' not in request.args or 'lon' not in request.args:
    resp = make_response(json.dumps({
      'error': 'Querystring params lat and lon are required'
    }))
    resp.headers['Content-Type'] = 'application/json'
    return resp

  model = Model(float(request.args.get('lat')), 
    float(request.args.get('lon')))
  
  score = model.generate_crime_score()
  (violent, nonviolent) = model.generate_partitioned_score()
  history = model.generate_monthly_score()

  recent = [c.dict() for c in model.get_recent()]

  return jsonify({'score': {
    'combined': score,
    'violent': violent,
    'nonviolent': nonviolent,
    'historical': history
  }, 'recent': recent})

@app.route('/demo/')
def demo():
  from pygeocoder import Geocoder
  
  locations = [
    '618 Rodman St, Philadelphia PA',
    '13th & Walnut St, Philadelphia, PA',
    '8600 Germantown Ave, Philadelphia, PA',
    '2929 Arch St, Philadelphia, PA',
    '332 South Smedley St, Philadelphia, PA',
    'Broad & Snyder St, Philadelphia, PA',
    '52nd & Market St, Philadelphia, PA',
    'Kensington & Somerset St, Philadelphia, PA'
  ]

  output = ''
  for location in locations:
    (lat, lon) = Geocoder.geocode(location)[0].coordinates
    model = Model(lat, lon)
    output += '%s\t%s\t%s<br/>' % (location, model.generate_crime_score(), model.get_simple_count())

  return output

if __name__ == '__main__':
  app.run(debug = True)
