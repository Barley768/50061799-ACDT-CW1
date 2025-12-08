import requests
from datetime import datetime

baseUrl = "https://api.open-meteo.com/v1/forecast"
params = {"latitude": 10.10, "longitude": 20.20, "hourly": "temperature_2m"}

response = requests.get(baseUrl, params=params, timeout=10)
print(f"Status code: {response.status_code}")

if response.ok:
    data = response.json()
    times = data["hourly"]["time"][:5]
    temps = data["hourly"]["temperature_2m"][:5]
    for t, temp in zip(times, temps):
        dt = datetime.fromisoformat(t)
        date = dt.strftime("%d-%m-%Y")
        time = dt.strftime("%H:%M")
        print(f"{date} {time} -> {temp} *C")
else:
    print(f"Error: {response.text}")
