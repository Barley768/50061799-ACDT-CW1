import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from API.API_wrapper import *


class ACDTApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Dashboard")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")
        self.state("zoomed")

        self.weather_canvas = None
        self.temp_canvas = None

        self.build_ui()

    def build_ui(self):
        # Top frame
        input_frame = ttk.Frame(self, padding=10)
        input_frame.pack(side=tk.TOP, fill=tk.X)

        # Origin point entry
        ttk.Label(input_frame, text="Origin:").grid(row=0, column=0, sticky="w")
        self.origin_entry = ttk.Entry(input_frame, width=30)
        self.origin_entry.grid(row=0, column=1, padx=5, pady=2)
        self.origin_entry.insert(0, "London, UK")

        # Destination point entry
        ttk.Label(input_frame, text="Destination:").grid(row=1, column=0, sticky="w")
        self.destination_entry = ttk.Entry(input_frame, width=30)
        self.destination_entry.grid(row=1, column=1, padx=5, pady=2)
        self.destination_entry.insert(0, "Berlin, Germany")

        # Year entry
        ttk.Label(input_frame, text="Year for holidays:").grid(
            row=2, column=0, sticky="w"
        )
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=2, column=1, padx=5, pady=2)
        self.year_entry.insert(0, "2025")

        # Route info button
        route_button = ttk.Button(
            input_frame, text="Analyse Route", command=self.on_route_button
        )
        route_button.grid(row=0, column=2, rowspan=3, padx=10)

        input_frame.columnconfigure(1, weight=1)

        # Middle Frame
        results_frame = ttk.LabelFrame(self, text="Route & Country Info", padding=10)
        results_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.route_label = ttk.Label(results_frame, text="Route: (no data yet)")
        self.route_label.pack(anchor="w")

        self.country_label = ttk.Label(
            results_frame, text="Country info: (no data yet)"
        )
        self.country_label.pack(anchor="w", pady=(5, 0))

        self.holidays_label = ttk.Label(
            results_frame, text="Upcoming Holidays: (no data yet)"
        )
        self.holidays_label.pack(anchor="w", pady=(5, 0))

        # Bottom Frame
        tab_frame = ttk.Frame(self)
        tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab = ttk.Notebook(tab_frame)
        self.tab.pack(fill=tk.BOTH, expand=True)

        # Tab 1
        self.dest_temp_frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(self.dest_temp_frame, text= "Destination Temperature Forecast")

        # Tab 2
        self.compare_temp_frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(self.compare_temp_frame, text="Origin Temp vs Destination Temp")
        
        #chart_frame = ttk.LabelFrame(
        #    self, text="Destination Tempurature Forecast", padding=10
        #)
        #chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        #self.chart_frame = chart_frame

    # Route info button function
    def on_route_button(self):
        origin = self.origin_entry.get().strip()
        destination = self.destination_entry.get().strip()
        year_text = self.year_entry.get().strip()

        if not origin or not destination:
            messagebox.showerror(
                "Input error",
                "Please enter both origin location and destination location",
            )
            return

        # Year validation
        try:
            year = int(year_text)
        except ValueError:
            messagebox.showerror(
                "Input error", "Please enter a valid integer for Year."
            )
            return

        # Get geocode origin and destination
        try:
            origin_geo = get_first_geocode(origin)
            dest_geo = get_first_geocode(destination)

            # Debug Printing
            print("\n -- Geocoding Results --")
            print(f"origin_geo = {origin_geo} TYPE = {type(origin_geo)}")
            print(f"dest_geo = {dest_geo} TYPE = {type(dest_geo)}")

            if origin_geo is None or dest_geo is None:
                messagebox.showerror(
                    "Geocoding error",
                    "Could not convert one or both of the locations into Latitude and Longitude",
                )
                return

            # Debug Printing
            print("\n--- DEBUG: Route Summary Input ---")
            print(f"Origin lat/lng: {origin_geo.get('lat')} {origin_geo.get('lng')}")
            print(f"Dest   lat/lng: {dest_geo.get('lat')} {dest_geo.get('lng')}")

            # Summarise route
            route = get_route_summary(
                start_lat=origin_geo["lat"],
                start_lon=origin_geo["lng"],
                end_lat=dest_geo["lat"],
                end_lon=dest_geo["lng"],
            )

            # Debug Printing
            print("\n--- DEBUG: Route Summary Output ---")
            print(f"route = {route} TYPE = {type(route)}")

            # Weather details
            origin_weather = get_weather(origin_geo["lat"], origin_geo["lng"], hours=24)
            dest_weather = get_weather(dest_geo["lat"], dest_geo["lng"], hours=24)

            # Destination country info
            dest_country_name = dest_geo["components"].get("country", destination)
            country_info = get_country(dest_country_name)

            # Debug Printing
            print("\n--- DEBUG: Country Info ---")
            print(f"country_info = {country_info} TYPE = {type(country_info)}")

            holidays = get_holidays(year, country_info["country_code"])

            # Debug Printing
            print("\n--- DEBUG: Holidays ---")
            print(f"holidays = {holidays} TYPE = {type(holidays)}")
            if holidays:
                print(
                    f"First holiday element: {holidays[0]} TYPE = {type(holidays[0])}"
                )

            # Update ui labels
            self.update_ui(origin_geo, dest_geo, route, country_info, holidays)

            # plot weather
            self.plot_weather(dest_weather)
            self.plot_compare_weather(
                origin_weather
                , dest_weather
                , origin_label = origin_geo["formatted"]
                , dest_label = dest_geo["formatted"]
            )

        except API_Error as e:
            messagebox.showerror("API error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected error", f"{type(e).__name__}: {e}")

    # Update ui labels
    def update_ui(self, origin_geo, dest_geo, route, country_info, holidays):
        route_text = (
            f"Origin: {origin_geo['formatted']} "
            f"({origin_geo['lat']:.4f}, {origin_geo['lng']:.4f})\n"
            f"Destination: {dest_geo['formatted']} "
            f"({dest_geo['lat']:.4f}, {dest_geo['lng']:.4f})\n"
            f"Distance: {route['distance_km']:.1f} km "
            f"Estimated duration: {route['duration_min']:.1f} minutes"
        )
        self.route_label.config(text=route_text)

        country_text = (
            f"Destination country: {country_info.get('name')} "
            f"({country_info.get('country_code')}) | "
            f"Region: {country_info.get('region')} / {country_info.get('subregion')}\n"
            f"Capital: {country_info.get('capital')} |"
            f"Population: {country_info.get('population')} | "
            f"Timezones: {', '.join(country_info.get('timezones', []))}\n"
            f"Currencies: {', '.join(country_info.get('currencies', []))} | "
            f"Languages: {', '.join(country_info.get('languages', []))}"
        )
        self.country_label.config(text=country_text)

        if holidays:
            preview = holidays[:5]
            hol_lines = [f"{h['date']} - {h['localName']}" for h in preview]
            holidays_text = "Upcoming holidays:\n" + "\n".join(hol_lines)
        else:
            holidays_text = "Upcoming holidays: None found for this year."

        self.holidays_label.config(text=holidays_text)

    # Plot weather into chart TAB 1
    def plot_weather(self, weather: dict):
        times = weather.get("times", [])
        temps = weather.get("temperature", [])

        if not times or not temps:
            messagebox.showwarning("Weather", "No weather data available to plot.")
            return

        if self.weather_canvas is not None:
            self.weather_canvas.get_tk_widget().destroy()
            self.weather_canvas = None

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Make time more readable
        short_times = []
        for t in times:
            if isinstance(t, str) and "T" in t:
                short_times.append(t.split("T")[1])
            else:
                short_times.append(str(t))

        ax.plot(short_times, temps, marker="o")
        ax.set_title("Temperature forecast (next 24h)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temperature (°C)")
        ax.tick_params(axis="x", rotation=45)

        fig.tight_layout()

        self.weather_canvas = FigureCanvasTkAgg(fig, master=self.dest_temp_frame)
        self.weather_canvas.draw()
        self.weather_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Plot Weather comparison into chart TAB 2
    def plot_compare_weather(self, origin_weather: dict, dest_weather: dict,
                             origin_label: str, dest_label: str):
        origin_times = origin_weather.get("times", [])
        origin_temps = origin_weather.get("temperature", [])

        dest_times = dest_weather.get("times", [])
        dest_temps = dest_weather.get("temperature", [])

        if not origin_times or not origin_temps or not dest_times or not dest_temps:
            messagebox.showwarning("Weather comparison", "Not enough weather data to compare.")
            return
        
        # Match length for comparison
        n = min(len(origin_temps), len(dest_temps))
        origin_temps = origin_temps[:n]
        dest_temps = dest_temps[:n]

        x_values = list(range(n))

        if self.temp_canvas is not None:
            self.temp_canvas.get_tk_widget().destroy()
            self.temp_canvas = None

        fig = Figure(figsize=(6,3), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(x_values, origin_temps, marker="o", label=f"Origin: {origin_label}")
        ax.plot(x_values, dest_temps, marker="o", linestyle="--", label=f"Destination: {dest_label}")

        ax.set_title("Temperature comparison (next 24h)")
        ax.set_xlabel("Hours from now")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)

        fig.tight_layout()

        self.compare_canvas = FigureCanvasTkAgg(fig, master=self.compare_temp_frame)
        self.compare_canvas.draw()
        self.compare_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = ACDTApp()
    app.mainloop()
