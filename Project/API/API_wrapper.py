from typing import List, Optional
import requests

# API Keys

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImY5ZTEyZDM1ZmU4OTQ2ZWViN2QwYjI4M2Q4OGM4OWQwIiwiaCI6Im11cm11cjY0In0="
OPENCAGE_API_KEY = "d863673d7e8647139b4face8079ed7ff"

# Error Handling

class API_Error(Exception):
    pass

def API_Get(url: str, *, params: dict | None = None, headers: dict | None = None, timeout: int = 10) -> dict:
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise API_Error(f"Request to {url} timed out") from exc
    except requests.exceptions.RequestException as exc:
        raise API_Error(f"Network error calling {url}: {exc}") from exc
    
    if not response.ok:
        try:
            err_JSON = response.json()
        except ValueError:
            err_JSON = response.text
        raise API_Error(f"HTTP {response.status_code} error from {url}: {err_JSON}")
    
    try:
        return response.json()
    except ValueError as exc:
        raise API_Error(f"Invalid JSON response from {url}") from exc

# Rest Countries API

countryBase = "https://restcountries.com/v3.1"

def get_country(name: str) -> dict:
    url = f"{countryBase}/name/{name}"
    data = API_Get(url)

    if not data:
        raise API_Error(f"No country data found for '{name}'.")
    
    raw = data[0]
    return {
        "name" : raw.get("name", {}).get("common")
        , "official_name" : raw.get("name", {}).get("official")
        , "country_code" : raw.get("cca2")
        , "region" : raw.get("region")
        , "subregion" : raw.get("subregion")
        , "capital" : (raw.get("capital") or ["Unknown"])[0]
        , "population" : raw.get("population")
        , "timezones" : raw.get("timezones", [])
        , "currencies" : list((raw.get("currencies") or {}).keys())
        , "languages" : list((raw.get("languages") or {}).values())
    }

# Open Meteo API

openMeteoBase = "https://api.open-meteo.com/v1/forecast"

def get_weather(latitude: float, longitude: float,
                hourly_params: str = "temperature_2m,precipitation,wind_speed_10m",
                hours: int= 24) -> dict:
    
    params = {
        "latitude" : latitude
        , "longitude" : longitude
        , "hourly" : hourly_params
        , "forecast_days" : 2
        , "timezone" : "auto"
    }
    data = API_Get(openMeteoBase, params=params)

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])[:hours]
    temps = hourly.get("temperature_2m", [])[:hours]
    precip = hourly.get("precipitation", [])[:hours]
    wind = hourly.get("wind_speed_10m", [])[:hours]

    return {
        "latitude" : data.get("latitude")
        , "longitude" : data.get("longitude")
        , "times" : times
        , "temperature" : temps
        , "precipitation" : precip
        , "wind_speed" : wind
    }


# Nager.Date API

nagerBase = "https://date.nager.at/api/v3"

def get_holidays(year: int, country_code: str) -> List[dict]:
    url = f"{nagerBase}/PublicHolidays/{year}/{country_code}"
    data = API_Get(url)
    return data

def get_upcoming_holidays(year: int, country_code: str, limit: int = 5) -> List[dict]:
    holidays = get_holidays(year, country_code)
    return holidays[:limit]

# Open Route Service API

ORSBase = "https://api.openrouteservice.org/v2/directions/driving-car"

def get_route_summary(start_lon: float, start_lat: float, 
                      end_lon: float, end_lat: float) -> dict:
    
    api_key = ORS_API_KEY
    if not api_key:
        raise API_Error("Missing ORS_API_KEY variable")
    
    params = {
        "api_key" : api_key
        , "start" : f"{start_lon},{start_lat}"
        , "end" : f"{end_lon},{end_lat}"
    }
    data = API_Get(ORSBase, params=params)

    try:
        feature = data["features"][0]
        summary = feature["properties"]["summary"]
    except (KeyError, IndexError) as exc:
        raise API_Error(f"Unexpected ORS response structure: {data}") from exc
    
    distance_m = summary.get("distance", 0)
    duration_s = summary.get("duration", 0)

    return {
        "distance_m" : distance_m
        , "distance_km" : distance_m / 1000.0
        , "duration_s" : duration_s
        , "duration_min" : duration_s / 60.0
    }

# OpenCage API

openCageBase = "https://api.opencagedata.com/geocode/v1/json"

def get_geocode(query: str, limit: int = 1) -> List[dict]:

    api_key = OPENCAGE_API_KEY
    if not api_key:
        raise API_Error("Missing OPENCAGE_API_KEY variable")
    
    params = {
        "q" : query
        , "key" : api_key
        , "limit" : limit
        , "no_annotations" : 1
    }
    data = API_Get(openCageBase, params=params)

    results: list[dict] = []
    for res in data.get("results", []):
        geom = res.get("geometry", {})
        results.append({
            "formatted" : res.get("formatted")
            , "lat" : geom.get("lat")
            , "lng" : geom.get("lng")
            , "components" : res.get("components", {})
        })
    return results

def get_first_geocode(query: str) -> Optional[dict]:
    results = get_geocode(query, limit=1)
    if not results:
        raise API_Error(f"No geocoding results for '{query}'")
    return results[0]