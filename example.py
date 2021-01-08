# Example code
# API Reference: http://open-notify.org/Open-Notify-API/ISS-Location-Now/

import urllib.request
import json

req = "http://api.open-notify.org/iss-now.json"
response = urllib.request.urlopen(req)
# print(response)
# <http.client.HTTPResponse object at 0x000001F439278AF0>

obj = json.loads(response.read())
# print(obj)
# {'timestamp': 1609538721, 'message': 'success', 'iss_position': {'latitude': '21.9538', 'longitude': '173.4064'}}

print(obj['timestamp'])
print(obj['iss_position']['latitude'], obj['iss_position']['longitude'])
# 1609538721
# 21.9538 173.4064

