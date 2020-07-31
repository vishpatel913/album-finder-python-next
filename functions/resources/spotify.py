import os
import sys
import json
import webbrowser
import difflib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from json.decoder import JSONDecodeError


class SpotifySearch:
    def __init__(self):
        print("Connecting...")
        username = "vish913@hotmail.co.uk"
        scope = "user-read-private user-read-playback-state user-modify-playback-state"

        auth_manager = SpotifyClientCredentials()
        try:
            self.spotifyObject = spotipy.Spotify(auth_manager=auth_manager)
            print("Connected to Spotify")
        except:
            print("Error connecting to Spotify")

        print()

    def getAlbums(self, artistQuery):
        searchQuery = "artist:" + artistQuery + " year:2020"
        searchResults = self.spotifyObject.search(searchQuery, 3, 0, "album")

        albums = searchResults['albums']['items']
        if not albums:
            return []

        artist = albums[0]['artists'][0]
        albumList = []
        print("SEARCHING ALBUMS BY: " + artistQuery)
        for album in albums:
            if album['album_type'] == 'album':
                string_diff = [li for li in difflib.ndiff(artist['name'].lower(), artistQuery.lower()) if li[0] != ' ']
                print('>> FOUND', album['name'], 'by', artist['name'])
                albumList.append({
                    'title': album['name'],
                    'artist': artist['name'],
                    'releaseDate': album['release_date'],
                    'url': album['external_urls']['spotify'],
                    'image': album['images'][1]['url'],
                    'acc': 1 - (len(string_diff) / len(artist['name'])),
                })

        return albumList
