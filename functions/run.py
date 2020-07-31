import os
import json
from handlers.albums_search_by_artists import main

from dotenv import load_dotenv
load_dotenv()

artists = os.listdir(os.path.expanduser(
    '~/Music/iTunes/Previous iTunes Libraries/Previous iTunes Libraries/iTunes Media/Music'))
event = {}
event['body'] = json.dumps({'artists': artists})

response = main(event=event, context={})
results = json.loads(response['body'])

try:
    output_path = './data/albums.json'
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile)
    print('Saved to', output_path)
except:
    with open('./tempOutput.json', 'x') as outfile:
        json.dump(results, outfile)
