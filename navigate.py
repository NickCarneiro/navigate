import json
import datetime
from flask import Flask, render_template, request
import flask
import requests
from pyquery import PyQuery as pq

app = Flask(__name__)

#unused endpoint that returns route data as json
@app.route('/routes')
def routes():
    destination = request.args.get('to', 'work')
    routes = scrape_commute_times(destination)
    json_response = json.dumps(routes, indent=4)
    return json_response

@app.route('/')
def home():
    time_str = datetime.datetime.now().strftime('%A %H:%M %p')
    destination = request.args.get('to', 'work')
    routes = scrape_commute_times(destination)
    if destination == 'work':
        reverse_direction = 'home'
    else:
        reverse_direction = 'work'
    reverse_url = '/?to={}'.format(reverse_direction)
    return render_template('index.html',
                           routes=routes,
                           time=time_str,
                           reverse_url=reverse_url,
                           destination=destination)


# returns a dict of dicts
def scrape_commute_times(destination):

    if destination == 'work':
        maps_url = 'https://maps.google.com/maps?saddr=2202+Delcrest+Drive,+Austin,+TX&daddr=7501+N+Capital+of+Texas+Hwy,+Austin,+TX&hl=en&ll=30.382057,-97.801323&spn=0.059827,0.362892&sll=30.245796,-97.774406&sspn=0.006682,0.01134&geocode=FaSDzQEduhQs-ikbDV1W17REhjHASmQvaN5BPQ%3BFcF5zwEdUf0r-ik1BGvSTctEhjE4r_XknZaZXg&oq=7501+n+capital&mra=ls&t=m&z=12'
    else:
        maps_url = 'https://maps.google.com/maps?saddr=7501+N+Capital+of+Texas+Hwy,+Austin,+TX&daddr=2202+Delcrest+Drive,+Austin,+TX&hl=en&sll=30.315099,-97.763557&sspn=0.213688,0.362892&geocode=FcF5zwEdUf0r-ik1BGvSTctEhjE4r_XknZaZXg%3BFaSDzQEduhQs-ikbDV1W17REhjHASmQvaN5BPQ&mra=ls&t=m&z=12'
    response = requests.get(maps_url)
    d = pq(response.content)
    route_names = d('.dir-altroute> div > div:nth-child(3)')
    distances = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(1)')
    usual_times = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(2)')
    current_times = d('.dir-altroute > div > div.altroute-rcol.altroute-aux > span')

    routes = []
    i = 0
    for route_name in route_names:
        route = {
            'route_name': route_name.text,
            'distance': distances[i].text,
            'usual_time': usual_times[i].text,
            'current_time': current_times[i].text.replace('In current traffic: ', '').strip()
        }
        routes.append(route)
        i += 1
    routes = sorted(routes, key=numberize_time)
    return routes


def numberize_time(route):
    time = route['usual_time']
    numerals = time.replace('mins', '')
    minutes_int = int(numerals)
    return minutes_int

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5555)

