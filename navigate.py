#!/usr/bin/env python

import datetime
import json
import flask
import requests

from flask import Flask, render_template, request
from pyquery import PyQuery as pq

app = Flask(__name__)

#unused endpoint that returns route data as json
@app.route('/routes')
def routes():
    destination = request.args.get('to', 'work')
    routes = scrape_commute_times(destination)
    return flask.Response(json.dumps(routes, indent=4),
                          mimetype='application/json')

@app.route('/')
def home():
    time_str = datetime.datetime.now().strftime('%A %I:%M %p')
    destination = request.args.get('to', 'work')
    routes = scrape_commute_times(destination)
    reverse_direction = 'home' if destination == 'work' else 'work'
    reverse_url = '/?to={}'.format(reverse_direction)
    return render_template('index.html',
                           routes=routes,
                           time=time_str,
                           reverse_url=reverse_url,
                           destination=destination)

# returns a list of dicts
def scrape_commute_times(destination):
    home = '2202 Delcrest Drive, Austin, TX'
    work = '7501 N Capital of Texas Hwy, Austin, TX'
    addrs = (home, work) if destination == 'work' else (work, home)
    maps_url = 'https://maps.google.com/maps?saddr={}&daddr={}'.format(
            *map(lambda s: s.replace(' ', '+'), addrs))

    d = pq(requests.get(maps_url).content)
    route_names = d('.dir-altroute> div > div:nth-child(3)')
    distances = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(1)')
    usual_times = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(2)')
    current_times = d('.dir-altroute > div > div.altroute-rcol.altroute-aux > span')

    def enumerate_routes(route_names):
        for i, route_name in enumerate(route_names):
            yield {'route_name': route_name.text,
                   'distance': distances[i].text,
                   'usual_time': usual_times[i].text,
                   'current_time': current_times[i].text.replace('In current traffic: ', '').strip()}

    def numberize_time(route):
        return int(route['usual_time'].replace('mins', ''))

    routes = list(enumerate_routes(route_names))
    return sorted(routes, key=numberize_time)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5555)

