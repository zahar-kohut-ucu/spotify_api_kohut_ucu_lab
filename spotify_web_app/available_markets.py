from dotenv import load_dotenv
import os
import base64
import json
import requests

import flask

import pycountry
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
import folium

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    '''
    Gets token from to have access to Spotify API.
    '''
    auth_string = client_id+':'+client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = requests.post(url, headers = headers, data = data, timeout=10)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token: str):
    '''
    Header for HTTP-request.
    '''
    return {'Authorization': 'Bearer ' + token}

def search_for_artists(token: str, name: str) -> dict:
    '''
    Creates and sends an GET_HTTP request to Spotify API.
    Returns JSON-file as Python-dictionary.
    '''
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f"?q={name}&type=track&limit=20"

    query_url = url + query
    result = requests.get(query_url, headers = headers, timeout=10)
    json_result = json.loads(result.content)
    return json_result

def parse_tracks(tracks: dict):
    '''
    Parse JSON-with tracks and creates an HTML-map.
    '''
    most_popular = sorted(tracks['tracks']['items'], key=lambda _x: _x['popularity'])[-1]
    markets = most_popular['available_markets']
    geolocator = Nominatim(user_agent="Kohut_Spotify_Map")
    locations = []

    for market in markets:
        country = pycountry.countries.get(alpha_2=market)
        if country:
            country = country.name
            try:
                location = geolocator.geocode(country)
            except GeocoderUnavailable:
                continue
            locations.append(([location.latitude, location.longitude], country))
        else:
            continue

    _map = folium.Map()
    for coords, name in locations:
        _map.add_child(folium.Marker(location=coords,
                                    popup=name,
                                    icon=folium.Icon(color='red')))

    _map.save('index.html')
