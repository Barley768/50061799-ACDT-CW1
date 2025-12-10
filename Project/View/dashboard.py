import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class dashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setup screensize
        self.title("Dashboard")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")
        self.state("zoomed")

        # Set references for Matplotlib
        self.weather_canvas = None
        self.temp_canvas = None
        self.holiday_canvas = None

        self.build_ui()

    def set_controller(self, controller):
        self.controller = controller

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

        # Analyse button
        route_button = ttk.Button(
            input_frame, text="Analyse Route", command=self.on_analyse_button
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

        # Tab 3
        self.holiday_chart_frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(self.holiday_chart_frame, text= "Holiday Frequency")

    # UI to Controller
    def on_analyse_button(self):
        if self.controller is not None:
            self.controller.on_analyse_route()

    def get_origin_input(self) -> str:
        return self.origin_entry.get().strip()
    
    def get_destination_input(self) -> str:
        return self.destination_entry.get().strip()
    
    def get_year(self) -> str:
        return self.year_entry.get().strip()
    
    # Controller calls to update UI
    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    # Update ui with data
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

    # Destroy stored canvas if it exists
    def destroy_canvas(self, canvas_attr: str):
        canvas = getattr(self, canvas_attr, None)
        if canvas is not None:
            try:
                canvas.get_tk_widget().destroy
            except Exception:
                pass
            setattr(self, canvas_attr, None)

    # Create Chart
    def new_chart(self, canvas_attr: str, master_frame, figsize=(6,3), dpi=100):
        self.destroy_canvas(canvas_attr)

        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        setattr(self, canvas_attr, canvas)

        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        return fig, ax

    # Plot weather into chart TAB 1
    def plot_weather(self, weather: dict):
        times = weather.get("times", [])
        temps = weather.get("temperature", [])

        if not times or not temps:
            self.show_warning("Weather", "No weather data available to plot.")
            return

        fig, ax = self.new_chart("weather_canvas", self.dest_temp_frame)

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

        self.weather_canvas.draw()

    # Plot Weather comparison into chart TAB 2
    def plot_compare_weather(self, origin_weather: dict, dest_weather: dict,
                             origin_label: str, dest_label: str):
        origin_times = origin_weather.get("times", [])
        origin_temps = origin_weather.get("temperature", [])

        dest_times = dest_weather.get("times", [])
        dest_temps = dest_weather.get("temperature", [])

        if not origin_times or not origin_temps or not dest_times or not dest_temps:
            self.show_warning("Weather comparison", "Not enough weather data to compare.")
            return
        
        # Match length for comparison
        n = min(len(origin_temps), len(dest_temps))
        origin_temps = origin_temps[:n]
        dest_temps = dest_temps[:n]
        x_values = list(range(n))

        fig, ax = self.new_chart("temp_canvas", self.compare_temp_frame)

        ax.plot(x_values, origin_temps, marker="o", label=f"Origin: {origin_label}")
        ax.plot(x_values, dest_temps, marker="o", linestyle="--", label=f"Destination: {dest_label}")

        ax.set_title("Temperature comparison (next 24h)")
        ax.set_xlabel("Hours from now")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)

        fig.tight_layout()

        self.temp_canvas.draw()

    # Plot Holiday frequency into chart TAB 3
    def plot_holiday_frequency(self, month_counts: list[int], month_labels: list[str], country_name: str, month_tooltips: list[str]):
        if not month_counts or not month_labels:
            self.show_warning("Holiday Frequency", "No holiday data available to plot.")
            return
        
        fig, ax = self.new_chart("holiday_canvas", self.holiday_chart_frame)

        fig.subplots_adjust(right=0.75, left=0.25)

        bars = ax.bar(month_labels, month_counts)

        ax.set_title(f"Public Holidays per month in {country_name}")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Holidays")
        ax.tick_params(axis="x", rotation=45)
        #fig.tight_layout()

        # Tooltip references
        self.holiday_fig = fig
        self.holiday_ax = ax
        self.holiday_bars = bars
        self.holiday_month_labels = month_labels
        self.holiday_month_counts = month_counts
        self.holiday_tooltips = month_tooltips

        annot = ax.annotate(
            ""
            , xy=(0,0)
            , xytext=(10, -25)
            , textcoords=("offset points")
            , bbox=dict(boxstyle="round", fc="white", ec="black", alpha=1.0)
            , arrowprops=dict(arrowstyle="->", color="black")
        )
        annot.set_visible(False)
        self.holiday_annot = annot

        # hover event
        def on_move(event):
            if event.inaxes == ax:
                visible = False
                for i, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        x = bar.get_x() + bar.get_width() / 2
                        y = bar.get_height()
                        annot.xy = (x,y)

                        label = month_labels[i]
                        count = month_counts[i]
                        tooltip = month_tooltips[i]

                        annot.set_text(f"{label}: {count} holidays\n{tooltip}")
                        annot.set_visible(True)
                        self.holiday_canvas.draw_idle()
                        visible=True
                        break
                
                if not visible and annot.get_visible():
                    annot.set_visible(False)
                    self.holiday_canvas.draw_idle()

        self.holiday_hover_cid = fig.canvas.mpl_connect("motion_notify_event", on_move)

        self.holiday_canvas.draw()