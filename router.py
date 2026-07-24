import flet as ft


class Router:
    def __init__(self, page):
        self.page = page
        self._views = {}

        self.current_view = None

        self.navbar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Dashboard", data="dashboard"),
                ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH, label="Calendar", data="calendar"),
            ],
        )
        self.navbar.on_change = self.navbar_change

    def register_view(self, name, view):
        self._views[name] = view

    def load_view(self, name):
        self.clear()

        if name in self._views:
            self.page.add(self._views[name])
            if hasattr(self._views[name], "on_load"):
                self._views[name].on_load()

        else:
            raise ValueError("Invalid view name, {}".format(name))

        self.page.add(self.navbar)

    def navbar_change(self, e):
        control: ft.NavigationBar = e.control
        self.page.clean()
        self.load_view(control.destinations[control.selected_index].data)

    def clear(self):
        self.page.clean()
