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

            month_counts, month_labels, month_tooltips = self.holiday_frequency(holidays)
            country_name = country_info.get("name", "Unknown Country")

            self.view.plot_holiday_frequency(month_counts, month_labels, country_name, month_tooltips)

        except API_Error as e:
            self.view.show_error("API error", str(e))
        except Exception as e:
            self.view.show_error("Unexpected error", f"{type(e).__name__}: {e}")

    def holiday_frequency(self, holidays: list[dict]) -> tuple[list[int], list[str], list[str]]:
        month_counts = [0] * 12
        month_holiday_names: list[list[str]] = [[] for _ in range(12)]

        for h in holidays:
            date_str = h.get("date", "")
            name = h.get("localName", h.get("name", "Unnamed holiday"))

            parts = date_str.split("-")
            if len(parts) >= 2:
                try:
                    month_index = int(parts[1]) - 1
                    if 0 <= month_index < 12:
                        month_counts[month_index] += 1
                        month_holiday_names[month_index].append(name)
                except ValueError:
                    continue

        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"
                        , "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Tooltip
        month_tooltips: list[str] = []
        for names in month_holiday_names:
            if not names:
                month_tooltips.append("No holidays")
            else:
                month_tooltips.append(", ".join(names))

        return month_counts, month_labels, month_tooltips
