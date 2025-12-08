import requests

API_Key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImY5ZTEyZDM1ZmU4OTQ2ZWViN2QwYjI4M2Q4OGM4OWQwIiwiaCI6Im11cm11cjY0In0="

baseUrl = "https://api.openrouteservice.org/v2/directions/driving-car"
params = {
    "api_key" : API_Key,
    "start" : "8.681495,49.41461",
    "end" : "8.687872,49.420318"
}

response = requests.get(baseUrl, params=params, timeout=10)
print(f"Status Code : {response.status_code}")

if response.ok:
    data = response.json()
    summary = data["features"][0]["properties"]["summary"]
    distance_km = summary["distance"] / 1000
    duration_min = summary["duration"] / 60
    print(f"Distance: {distance_km:.1f} km\nEstimated travel time: {duration_min:.1f} minutes")
else:
    print(f"Error: {response.text}")