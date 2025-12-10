"""
Docstring for dashboard:
This module creates the main GUI window for the application,
allowing for user input, updating results and drawing
tabbed data visualisation charts
"""

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from pathlib import Path
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage


class dashboard(tk.Tk):
    """Main application GUI for interacting with and visualising data"""
    def __init__(self):
        super().__init__()

        # Setup screensize
        self.title("Delivery Routing Analysis Application")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")
        self.state("zoomed")

        # Set references for Matplotlib
        self.weather_canvas = None
        self.temp_canvas = None
        self.holiday_canvas = None
        self.risk_canvas = None

        self.build_ui()

        # Output variables
        self.output_dir = Path("Project") / "Output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set smtp variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = "neil.acdt@gmail.com"
        self.smtp_password = "swyktnislasbjcif"
        self.smtp_from = "neil.acdt@gmail.com"

    def set_controller(self, controller):
        self.controller = controller

    def build_ui(self):
        """Builds all UI elements"""

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

        # Tab 4
        self.risk_chart_frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(self.risk_chart_frame, text="Delivery Risk")

        # export/email controls
        self.build_export_controls()
    
    # Export and Email
    def build_export_controls(self):
        export_frame = ttk.Frame(self, padding=10)
        export_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0,10))

        ttk.Button(
            export_frame
            , text="Save current chart"
            , command=self.save_current_tab
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame
            , text="Save all charts"
            , command=self.save_all_tabs
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(export_frame, text="Email report to:").pack(side=tk.LEFT, padx=(20, 5))

        self.email_entry = ttk.Entry(export_frame, width=30)
        self.email_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            export_frame
            , text="Send report"
            , command=self.email_report_from_ui
        ).pack(side=tk.LEFT, padx=5)

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

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    # Update ui with data
    def update_ui(self, origin_geo, dest_geo, route, country_info, holidays):
        """Updates UI labels after analysis"""

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
        """Removes any existing matplotlib canvas and tooltips"""

        canvas = getattr(self, canvas_attr, None)
        if canvas is not None:

            hover_map = {
                "holiday_canvas": "holiday_hover_cid",
                "weather_canvas": None,
                "temp_canvas": None,
                "risk_canvas": None
            }

            hover_attr = hover_map.get(canvas_attr)
            if hover_attr and hasattr(self, hover_attr):
                cid = getattr(self, hover_attr)
                try:
                    canvas.figure.canvas.mpl_disconnect(cid)
                except Exception:
                    pass
                setattr(self, hover_attr, None)

            try:
                canvas.get_tk_widget().destroy()
                fig = canvas.figure
                fig.clear()
                plt.close(fig)
            except Exception:
                pass
            setattr(self, canvas_attr, None)

    # Create Chart
    def new_chart(self, canvas_attr: str, master_frame, figsize=(6,3), dpi=100):
        """Create and draw new matplotlib charts"""

        self.destroy_canvas(canvas_attr)

        fig = Figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        setattr(self, canvas_attr, canvas)

        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return fig, ax
    
    def style_charts(self, ax, title: str | None = None, xlabel: str | None = None, ylabel: str | None = None):
        if title is not None:
            ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
        if xlabel is not None:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel is not None:
            ax.set_ylabel(ylabel, fontsize=10)

        ax.tick_params(axis="both", labelsize=9)

        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

        ax.margins(x=0.05, y=0.1)

    # Plot weather into chart TAB 1
    def plot_weather(self, weather: dict):
        """Plot the temperature forecast for the destination"""

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

        self.style_charts(
            ax
            , title= "Temperature forecast (next 24h)"
            , xlabel= "Time"
            , ylabel= "Temperature (°C)"
        )
        ax.tick_params(axis="x", rotation=45)

        fig.tight_layout()
        self.weather_canvas.draw()

    # Plot Weather comparison into chart TAB 2
    def plot_compare_weather(self, origin_weather: dict, dest_weather: dict,
                             origin_label: str, dest_label: str):
        """Compares the weather between origin and destination locations"""

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

        self.style_charts(
            ax
            , title= "Temperature comparison (next 24h)"
            , xlabel= "Hours from now"
            , ylabel= "Temperature (°C)"
        )
        ax.legend(fontsize=9)

        fig.tight_layout()
        self.temp_canvas.draw()

    # Plot Holiday frequency into chart TAB 3
    def plot_holiday_frequency(self, month_counts: list[int], month_labels: list[str], country_name: str, month_tooltips: list[str]):
        """Plot monthly holiday frequency and create tooltips for additional insight"""

        if not month_counts or not month_labels:
            self.show_warning("Holiday Frequency", "No holiday data available to plot.")
            return
        
        fig, ax = self.new_chart("holiday_canvas", self.holiday_chart_frame)

        fig.subplots_adjust(right=0.75, left=0.25)
        bars = ax.bar(month_labels, month_counts)

        self.style_charts(
        ax
        , title= f"Public Holidays per month in {country_name}"
        , xlabel= "Month"
        , ylabel= "Number of Holidays"
        )
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

    # Plot delivery risk score into chart TAB 4
    def plot_risk_score(self, risk_score: int, explanations: list[str]):
        """Plot delivery risk score and breakdown explanation text"""

        risk_score = max(0, min(int(risk_score), 100))

        fig, ax = self.new_chart("risk_canvas", self.risk_chart_frame, figsize=(6,2.5))

        ax.barh([0], [risk_score], height=0.4)

        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xticks([0, 25, 50, 75, 100])

        self.style_charts(
            ax
            , title="Delivery Risk Score"
            , xlabel="Risk (0 = Low, 100 = High)"
            , ylabel=None
        )

        ax.grid(False)

        ax.text(
            risk_score
            , 0
            , f"{risk_score}"
            , va="center"
            , ha="left"
            , fontsize=10
            , fontweight="bold"
        )

        if explanations:
            expl_title = "Risk Breakdown:"
            expl_text = "\n".join(explanations)
            fig.subplots_adjust(bottom=0.4)
            ax.text(
                0
                , -0.25
                , expl_title
                , transform=ax.transAxes
                , va="top"
                , ha="left"
                , fontsize=10
                , fontweight="bold"
                , wrap=True
            )
            ax.text(
                0
                , -0.35
                , expl_text
                , transform=ax.transAxes
                , va="top"
                , ha="left"
                , fontsize=8
                , wrap=True
            )

        self.risk_canvas.draw()

    # Save a single figure to Output
    def save_figure(self, fig, basename: str) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{basename}_{ts}.png"
        path = self.output_dir / filename
        fig.savefig(path, dpi=150, bbox_inches="tight")
        return path
    
    # Find current Tab for saving
    def get_current_tab(self):
        try:
            index = self.tab.index(self.tab.select())
        except Exception:
            return None, None
        
        if index == 0 and self.weather_canvas is not None:
            return self.weather_canvas.figure, "destination_temperature"
        elif index == 1 and self.temp_canvas is not None:
            return self.temp_canvas.figure, "temperature_comparison"
        elif index == 2 and self.holiday_canvas is not None:
            return self.holiday_canvas.figure, "holiday_frequency"
        elif index == 3 and self.risk_canvas is not None:
            return self.risk_canvas.figure, "delivery_risk"
        
        return None, None
    
    # Save current tab
    def save_current_tab(self):
        fig, basename = self.get_current_tab()
        if fig is None:
            self.show_warning("Export", "No chart to save on this tab")
            return
        
        path = self.save_figure(fig, basename)
        self.show_info("Export", f"Saved chart to:\n{path}")
    
    # Save all tabs
    def save_all_tabs(self):
        saved_paths = []

        if self.weather_canvas is not None:
            saved_paths.append(self.save_figure(self.weather_canvas.figure, "destination_temperature"))

        if self.temp_canvas is not None:
            saved_paths.append(self.save_figure(self.temp_canvas.figure, "temperature_comparison"))

        if self.holiday_canvas is not None:
            saved_paths.append(self.save_figure(self.holiday_canvas.figure, "holiday_frequency"))

        if self.risk_canvas is not None:
            saved_paths.append(self.save_figure(self.risk_canvas.figure, "delivery_risk"))

        if not saved_paths:
            self.show_warning("Export", "No charts are currently available to save.")
            return
        
        msg = "Saved:\n" + "\n".join(str(p) for p in saved_paths)
        self.show_info("Export", msg)

    # Create PDF with all charts
    def create_report_pdf(self) -> Path | None:
        figs= []

        if self.weather_canvas is not None:
            figs.append(self.weather_canvas.figure)

        if self.temp_canvas is not None:
            figs.append(self.temp_canvas.figure)

        if self.holiday_canvas is not None:
            figs.append(self.holiday_canvas.figure)

        if self.risk_canvas is not None:
            figs.append(self.risk_canvas.figure)

        if not figs:
            self.show_warning("Report", "No charts available to include in the report.")
            return None
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = self.output_dir / f"report_{ts}.pdf"

        with PdfPages(pdf_path) as pdf:
            for fig in figs:
                pdf.savefig(fig)

        return pdf_path
    
    # Email Report button function
    def email_report_from_ui(self):
        recipient = self.email_entry.get().strip()
        if not recipient:
            self.show_warning("Email", "Please enter a recipient email address.")
            return
        
        pdf_path = self.create_report_pdf()
        if pdf_path is None:
            return
        
        try:
            self.send_email_with_attachment(recipient, pdf_path)
        except Exception as e:
            self.show_error("Email", f"Failed to send email:\n{e}")
        else:
            self.show_info("Email", f"Report emailed to {recipient}")

    # Send email function
    def send_email_with_attachment(self, recipient: str, attachment_path: Path):
        msg = EmailMessage()
        msg["Subject"] = "Route and Logistics Report"
        msg["From"] = self.smtp_from
        msg["To"] = recipient
        msg.set_content("Attached is your latest route/logistics report from the ACDT dashboard.")

        with open(attachment_path, "rb") as f:
            data = f.read()

        msg.add_attachment(
            data
            , maintype="application"
            , subtype="pdf"
            , filename=os.path.basename(attachment_path)
        )

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)