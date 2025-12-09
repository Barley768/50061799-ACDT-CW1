from Models.logistics import logistics
from API.API_wrapper import API_Error
from View.dashboard import dashboard

class DashboardController:

    def __init__(self, model: logistics, view: dashboard):
        self.model = model
        self.view = view

    # Analyse button logic
    def on_analyse_route(self):
        origin = self.view.get_origin_input()
        destination = self.view.get_destination_input()
        year_text = self.view.get_year()
        
        # Location validation
        if not origin or not destination:
            self.view.show_error(
                "Input error",
                "Please enter both origin location and destination location",
            )
            return

        # Year validation
        try:
            year = int(year_text)
        except ValueError:
            self.view.show_error(
                "Input error", "Please enter a valid integer for Year."
            )
            return
        
        try:
            data = self.model.analyse_route(origin, destination, year, hours=24)

            origin_geo = data["origin_geo"]
            dest_geo = data["dest_geo"]
            route = data["route"]
            origin_weather = data["origin_weather"]
            dest_weather = data["dest_weather"]
            country_info = data["country_info"]
            holidays = data["holidays"]

            self.view.update_ui(origin_geo, dest_geo, route, country_info, holidays)

            self.view.plot_weather(dest_weather)
            self.view.plot_compare_weather(
                origin_weather
                , dest_weather
                , origin_label=origin_geo["formatted"]
                , dest_label=dest_geo["formatted"]
            )

        except API_Error as e:
            self.view.show_error("API error", str(e))
        except Exception as e:
            self.view.show_error("Unexpected error", f"{type(e).__name__}: {e}")
