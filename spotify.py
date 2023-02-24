from dotenv import load_dotenv
import os
import base64
import json
import requests

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

def search_for_artists(token: str, _type: str, name: str, limit: int) -> dict:
    '''
    Creates and sends an GET_HTTP request to Spotify API.
    Returns JSON-file as Python-dictionary.
    >>> search_for_artists(get_token(), 'artist', 'rammstein', 1)['artists']['items'][0]['type']
    'artist'
    '''
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f"?q={name}&type={_type}&market=ua&limit={limit}"

    query_url = url + query
    result = requests.get(query_url, headers = headers, timeout=10)
    json_result = json.loads(result.content)
    return json_result

def parse_artist(artist: str, infotype: str) -> str: 
    '''
    Parse JSON-file from Spotify API.
    Possible types of information:
    name - artist full name
    link - link for artist Spotify page
    genres - artist genres
    popularity - artist popularity in Ukraine
    tracks - artist's 10 most popular tracks
    >>> parse_artist('rhcp', 'link')
    'https://open.spotify.com/artist/0L8ExT028jH3ddEcZwqJJ5'
    '''
    token = get_token()
    if infotype == 'tracks':
        data = search_for_artists(token, 'track', artist, 20)['tracks']['items']
        top = sorted([(_x['popularity'], _x['name']) for _x in data])[10:]
        return list(zip(*top))[1]
    else:
        data = search_for_artists(token, 'artist', artist, 1)['artists']['items'][0]
        if infotype == 'link':
            return data['external_urls']['spotify']
        else:
            return data[infotype]
