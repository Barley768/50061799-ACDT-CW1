"""
Docstring for dashboard_controller:
This module holds the interactions between the logistics model and
the Tkinter dashboard view. Covers user input, API calls, and
calculates holiday frequency and delivery risk score
"""

from Models.logistics import logistics
from API.API_wrapper import API_Error
from View.dashboard import dashboard

class DashboardController:
    """Holds interactions between logistics model and tkinter dashboard"""

    def __init__(self, model: logistics, view: dashboard):
        self.model = model
        self.view = view

    # Analyse button logic
    def on_analyse_route(self):
        """Takes user input, performs route analysis then updates the UI"""

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

            # Tab 1
            self.view.plot_weather(dest_weather)

            # Tab 2
            self.view.plot_compare_weather(
                origin_weather
                , dest_weather
                , origin_label=origin_geo["formatted"]
                , dest_label=dest_geo["formatted"]
            )

            # Tab 3
            month_counts, month_labels, month_tooltips = self.holiday_frequency(holidays)
            country_name = country_info.get("name", "Unknown Country")
            self.view.plot_holiday_frequency(month_counts, month_labels, country_name, month_tooltips)

            # Tab 4
            risk_score, risk_explanations = self.compute_risk_score(route, dest_weather, holidays)
            self.view.plot_risk_score(risk_score, risk_explanations)

        except API_Error as e:
            self.view.show_error("API error", str(e))
        except Exception as e:
            self.view.show_error("Unexpected error", f"{type(e).__name__}: {e}")

    def holiday_frequency(self, holidays: list[dict]) -> tuple[list[int], list[str], list[str]]:
        """Takes user input, counts holidays per month and generates tooltips"""

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
    
    def compute_risk_score(self, route: dict, dest_weather: dict, holidays: list[dict]) -> tuple[int, list[str]]:
        """Calculates a delivery risk score based on distance, weather and public holidays"""

        explanations: list[str] = []

        # Distance impact
        distance_km = route.get("distance_km", 0) or 0
        distance_factor = min(distance_km / 2000.0, 1.0) # 2000km or above is max risk
        explanations.append(f"Distance: {distance_km:.0f} km")

        # Weather impact
        temps = dest_weather.get("temperature", []) or []
        if temps:
            t_min = min(temps)
            t_max = max(temps)
            temp_range = t_max - t_min

            volatility_factor = min(temp_range / 15.0, 1.0)

            cold_factor = 0.0
            if t_min <= 0:
                cold_factor = 0.3

            weather_factor = min(volatility_factor + cold_factor, 1.0)

            explanations.append(
                f"Temperature range: {t_min:.1f}°C to {t_max:.1f}°C "
                f"(Range {temp_range:.1f}°C)"
            )
            if cold_factor > 0:
                explanations.append("Cold conditions detected (<= 0°C).")
        else:
            weather_factor = 0.0
            explanations.append("No temperature data avaialble, weather risk not considered.")
        
        # Holidays impact
        total_holidays = len(holidays)
        holiday_factor = min(total_holidays / 20.0, 1.0) # Max holiday risk at 20
        explanations.append(f"Total public holidays this year: {total_holidays}")

        raw_score = (
            40.0 * distance_factor +
            40.0 * weather_factor +
            20.0 * holiday_factor
        )

        score = int(round(max(0.0, min(raw_score, 100.0))))

        explanations.append(f"Weighted risk score (0-100): {score}")

        return score, explanations
