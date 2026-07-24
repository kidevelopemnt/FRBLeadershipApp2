import flet as ft

from datetime import datetime, timedelta
import calendar

from models import Event


class CalendarView(ft.Column):

    def __init__(self, page, router, user):
        self.app_page = page
        self.router = router
        self.user = user

        self.current_date = datetime.now()

        super().__init__(
            expand=True,
            spacing=10
        )

        self.calendar_grid = ft.Column(
            expand=True
        )

        self.build()

    def on_load(self):
        self.render_calendar()

    def build(self, render=False):
        self.controls.clear()

        self.controls.append(
            self.header()
        )

        self.controls.append(
            self.calendar_grid
        )

        if render:
            self.render_calendar()



    def header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[

                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    on_click=self.previous_month
                ),

                ft.Text(
                    self.current_date.strftime("%B %Y"),
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),

                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    on_click=self.next_month
                )

            ]
        )



    def render_calendar(self):
        self.calendar_grid.controls.clear()

        # Weekday header
        self.calendar_grid.controls.append(
            ft.Row(
                controls=[
                    ft.Text(
                        day,
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    )
                    for day in
                    [
                        "Sun",
                        "Mon",
                        "Tue",
                        "Wed",
                        "Thu",
                        "Fri",
                        "Sat"
                    ]
                ]
            )
        )

        month = self.current_date.month
        year = self.current_date.year

        first_day = datetime(
            year,
            month,
            1
        )

        start = first_day - timedelta(
            days=first_day.weekday() + 1
        )

        rows = []
        current = start

        for week in range(6):
            days = []

            for day in range(7):
                days.append(
                    self.day_cell(current)
                )
                current += timedelta(days=1)


            rows.append(
                ft.Row(
                    controls=days,
                    expand=True
                )
            )

        self.calendar_grid.controls.extend(rows)
        self.update()


    def day_cell(self, date):
        events = self.events_on_date(date)

        event_controls = []

        for event in events:
            event_controls.append(
                ft.Container(
                    bgcolor=ft.Colors.BLUE_100,
                    padding=5,
                    border_radius=5,
                    content=ft.Text(
                        event.name,
                        size=11,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    on_click=lambda e, ev=event:
                        self.open_event(ev)
                )
            )

        return ft.Container(
            height=100,
            expand=True,
            border=ft.border.Border.all(
                1,
                ft.Colors.GREY_300
            ),
            padding=5,
            content=ft.Column(
                controls=[
                    ft.Text(
                        str(date.day),
                        weight=ft.FontWeight.BOLD
                    ),
                    *event_controls
                ]
            )
        )

    def events_on_date(self, date):
        events = []

        for event in Event.objects.all():
            if event.start_dt:
                if (
                    event.start_dt.year == date.year
                    and event.start_dt.month == date.month
                    and event.start_dt.day == date.day
                ):
                    events.append(event)


        return events

    def previous_month(self, e):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(
                year=self.current_date.year - 1,
                month=12
            )
        else:
            self.current_date = self.current_date.replace(
                month=self.current_date.month - 1
            )


        self.build(True)
        self.update()

    def next_month(self, e):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(
                year=self.current_date.year + 1,
                month=1
            )
        else:
            self.current_date = self.current_date.replace(
                month=self.current_date.month + 1
            )

        self.build(True)
        self.update()

    def open_event(self, event):
        from views.event_view import EventView

        self.app_page.clean()
        self.app_page.add(
            EventView(
                self.app_page,
                self.user,
                event
            )
        )
        self.router.draw_navbar()