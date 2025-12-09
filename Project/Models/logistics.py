from API.API_wrapper import (
    get_first_geocode
    , get_route_summary
    , get_weather
    , get_country
    , get_holidays
    , API_Error
)

class logistics:

    def analyse_route(self, origin: str, destination: str, year: int, hours: int = 24) -> dict:
        # Geocoding
        origin_geo = get_first_geocode(origin)
        dest_geo = get_first_geocode(destination)

        if origin_geo is None or dest_geo is None:
            raise API_Error("Could not convert one or both locations into latitude/longitude")
        
        # Route lat/lng
        route = get_route_summary(
            start_lat=origin_geo["lat"]
            , start_lon=origin_geo["lng"]
            , end_lat=dest_geo["lat"]
            , end_lon=dest_geo["lng"]
        )

        # Weather
        origin_weather = get_weather(origin_geo["lat"], origin_geo["lng"], hours=hours)
        dest_weather = get_weather(dest_geo["lat"], dest_geo["lng"], hours=hours)

        # Dest Country Info
        dest_country_name = dest_geo["components"].get("country", destination)
        country_info = get_country(dest_country_name)

        # Holidays for year
        country_code = country_info.get("country_code")
        if not country_code:
            raise API_Error("Destination country code not found - can't find holidays")
        
        holidays = get_holidays(year, country_code)

        return {
            "origin_geo" : origin_geo
            , "dest_geo" : dest_geo
            , "route" : route
            , "origin_weather" : origin_weather
            , "dest_weather" : dest_weather
            , "country_info" : country_info
            , "holidays" : holidays
        }
