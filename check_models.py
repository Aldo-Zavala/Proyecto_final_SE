import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv('gemini.env')

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/models',
    headers={'Authorization': 'Bearer ' + os.getenv('OPENROUTER_API_KEY')}
)

data = json.loads(urllib.request.urlopen(req).read())

gratis = [m['id'] for m in data['data'] if m.get('pricing', {}).get('prompt', '1') == '0']

print('MODELOS GRATUITOS DISPONIBLES:')
for m in gratis[:15]:
    print('-', m)
    