"""
Docstring for main
This is the main script that connects the logistics model,
dashboard GUI and controller, then draws the tkinter GUI
"""

from Models.logistics import logistics
from View.dashboard import dashboard
from Controllers.dashboard_controller import DashboardController

def main():
    model = logistics()
    view = dashboard()
    controller = DashboardController(model, view)
    view.set_controller(controller)

    view.mainloop()

if __name__ == "__main__":
    main()