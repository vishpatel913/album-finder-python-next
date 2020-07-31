import setup

import json
import os
import logging
from resources.spotify import SpotifySearch


def build_response(code, body):
    response = {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
    return response


def main(event, context):
    data = json.loads(event["body"])
    artist_list = data["artists"]

    app = SpotifySearch()
    results = []
    for artist in artist_list:
        albums = app.getAlbums(artist)
        results.extend(albums)

    return build_response(200, results)
