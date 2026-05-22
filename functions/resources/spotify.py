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

    def getAlbumsById(self, artist_id, year=2020):
        """Fetch albums for a known Spotify artist ID via /artists/{id}/albums.

        Avoids the search-result ambiguity of `getAlbums(name)` — once you have
        an ID you can hit the artist directly. Filters to release-year `year`
        and `album` type (drops singles/compilations).
        """
        response = self.spotifyObject.artist_albums(artist_id, album_type='album', limit=50)
        items = response.get('items', [])
        if not items:
            return []

        artist_name = items[0]['artists'][0]['name'] if items[0].get('artists') else ''
        print("SEARCHING ALBUMS BY ID:", artist_id, "—", artist_name)

        albumList = []
        for album in items:
            release_date = album.get('release_date', '')
            if not release_date.startswith(str(year)):
                continue
            images = album.get('images') or []
            image_url = images[1]['url'] if len(images) > 1 else (images[0]['url'] if images else '')
            print('>> FOUND', album['name'], 'by', artist_name)
            albumList.append({
                'title': album['name'],
                'artist': artist_name,
                'releaseDate': release_date,
                'url': album['external_urls']['spotify'],
                'image': image_url,
            })

        return albumList
