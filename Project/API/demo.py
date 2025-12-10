"""
Docstring for demo:
Test document to validate API usage from API_wrapper
"""

from API.API_wrapper import (
    API_Error
    , get_country
    , get_weather
    , get_holidays
    , get_route_summary
    , get_first_geocode
)

def demo():
    try:
        origin = "London, UK"
        destination = "Berlin, Germany"
        origin_geo = get_first_geocode(origin)
        dest_geo = get_first_geocode(destination)

        if origin_geo is None or dest_geo is None:
            print("Could not find one of the locations")
            return
        
        print(f"Origin: {origin_geo['formatted']} {origin_geo['lat']} {origin_geo['lng']}")
        print(f"Destination: {dest_geo['formatted']} {dest_geo['lat']} {dest_geo['lng']}")

        route = get_route_summary(
            start_lon=origin_geo["lng"], start_lat=origin_geo["lat"]
            , end_lon=dest_geo["lng"], end_lat=dest_geo["lat"]
        )
        print(f"Distance: {route['distance_km']:.1f} km")
        print(f"Duration: {route['duration_min']:.1f} minutes")

        weather = get_weather(dest_geo["lat"], dest_geo["lng"], hours=12)
        print("First few weather points:")
        for t, temp in zip(weather["times"][:5], weather["temperature"][:5]):
            print(f"{t} -> {temp} °C")

        dest_country = get_country("Germany")
        print(f"Country info: {dest_country}")

        holidays = get_holidays(2025, dest_country["country_code"])
        print("First 3 holidays:")
        for h in holidays[:3]:
            print(f"{h['date']} - {h["localName"]}")
        
    except API_Error as e:
        print(f"API error: {e}")

if __name__ == "__main__":
    demo()