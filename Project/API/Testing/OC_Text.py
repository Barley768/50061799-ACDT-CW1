import requests

API_Key = "d863673d7e8647139b4face8079ed7ff"

baseUrl = "https://api.opencagedata.com/geocode/v1/json"
params = {
    "q" : "Belfast, UK",
    "key" : API_Key,
    "limit" : 1
}

response = requests.get(baseUrl, params=params, timeout=10)
print(f"Status code: {response.status_code}")

if response.ok:
    data = response.json()
    if data["results"]:
        result = data["results"][0]
        lat = result["geometry"]["lat"]
        lng = result["geometry"]["lng"]
        formatted = result["formatted"]
        print(f"Found: {formatted}\nLat/Lng: {lat} {lng}")
    else:
        print("No results found.")
else:
    print(f"Error: {response.text}")