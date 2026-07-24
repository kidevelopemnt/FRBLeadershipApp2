import flet as ft

from models import User, Event, Tag, AttendanceRecord, AbsenceRequest
from router import Router

from views.calendar_view import CalendarView
from views.dashboard_view import DashboardView


def main(page: ft.Page):
    page.title = "Band Attendance"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    current_user = User.objects.all()[0]  # Replace with login later

    router = Router(page)

    dashboard = DashboardView(page, router, current_user)
    calendar = CalendarView(page, router, current_user)

    router.register_view("dashboard", dashboard)
    router.register_view("calendar", calendar)

    router.load_view("dashboard")

ft.run(main)
