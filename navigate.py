import json
from flask import Flask
import flask
import requests
from pyquery import PyQuery as pq

app = Flask(__name__)

@app.route("/")
def hello():
    routes = scrape_commute_times()
    print routes
    json_response = json.dumps(routes)
    return json_response


# returns a dict of dicts
def scrape_commute_times():

    response = requests.get('https://maps.google.com/maps?saddr=2202+Delcrest+Drive,+Austin,+TX&daddr=7501+N+Capital+of+Texas+Hwy,+Austin,+TX&hl=en&ll=30.382057,-97.801323&spn=0.059827,0.362892&sll=30.245796,-97.774406&sspn=0.006682,0.01134&geocode=FaSDzQEduhQs-ikbDV1W17REhjHASmQvaN5BPQ%3BFcF5zwEdUf0r-ik1BGvSTctEhjE4r_XknZaZXg&oq=7501+n+capital&mra=ls&t=m&z=12')
    d = pq(response.content)
    route_names = d('.dir-altroute> div > div:nth-child(3)')
    distances = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(1)')
    usual_times = d('.dir-altroute > div > div.altroute-rcol.altroute-info > span:nth-child(2)')
    current_times = d('.dir-altroute > div > div.altroute-rcol.altroute-aux > span')

    routes = {}
    i = 0
    for route_name in route_names:
        routes[route_name.text] = {
            'distance': distances[i].text,
            'usual_time': usual_times[i].text,
            'current_time': current_times[i].text.replace('In current traffic: ', '').strip()
        }
        i += 1
    return routes

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5555)

