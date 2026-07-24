from datetime import datetime

import flet as ft

from models import Event
from settings import DT_FORMAT, DATE_FORMAT


class DashboardView(ft.Column):
    def __init__(self, page, router, user):
        self.app_page = page
        self.router = router
        self.user = user

        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        self.build()

    def build(self):
        self.controls.clear()

        self.student_name_ipt = ft.TextField(label="Student Name", hint_text="e.x. Jane Doe", expand=True)
        self.reason_ipt = ft.TextField(label="Reason", hint_text="e.x. Doctor's Appointment", expand=True)

        self.absence_type_radio_group = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value="absent", label="Absence"),
                    ft.Radio(value="tardy", label="Tardy"),
                    ft.Radio(value="left_early", label="Leaving Early"),
                ]
            )
        )

        self.absence_duration_radio_group = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value="event", label="One Event"),
                    ft.Radio(value="time", label="Multiple Days"),
                ]
            ),
            on_change=self.absence_duration_changed,
        )

        self.date_range_picker = ft.DateRangePicker(
            first_date=datetime.today(),
        )
        self.date_range_picker.on_change = self.date_range_changed

        self.date_range_btn = ft.Button(
            "Select Range",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            expand=True,
            on_click=lambda e: self.page.show_dialog(self.date_range_picker),
            visible=False
        )

        self.event_dropdown = ft.Dropdown(
            label="Event",
            expand=True,
            options=[
                ft.DropdownOption(key=str(event.id),
                                  text=f"{event.name} ({event.start_dt.strftime(DT_FORMAT)} - {event.end_dt.strftime(DT_FORMAT)})")
                for event in Event.objects.filter(attendance_locked=False)
            ],
            visible=False
        )

        ## Add controls to screen

        self.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "FRB Attendance Dashboard",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    )
                ]
            )
        )

        self.controls.append(
            ft.Row(
                # wrap=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Chip(
                        label=ft.Text(tag.name),
                        bgcolor=tag.color,
                        color=tag.color,
                        on_select=lambda e: None,
                        show_checkmark=False
                    )
                    for tag in self.user.tags
                ]
            )
        )

        self.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Card(
                        expand=True,
                        content=ft.Container(
                            expand=True,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text(
                                                "Attendance Reports",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                text_align=ft.TextAlign.CENTER
                                            )
                                        ]
                                    )
                                ]
                            )
                        ),
                    ),
                    ft.Card(
                        expand=True,
                        content=ft.Container(
                            expand=True,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text(
                                                "Absence Requests",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                text_align=ft.TextAlign.CENTER
                                            )
                                        ]
                                    ),
                                    ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        margin=15,
                                        controls=[
                                            self.student_name_ipt,
                                            self.reason_ipt,

                                            ft.Row(
                                                controls=[
                                                    ft.Column(controls=[self.absence_type_radio_group]),
                                                    ft.VerticalDivider(),
                                                    ft.Column(controls=[self.absence_duration_radio_group]),
                                                ]
                                            ),

                                            ft.Row(
                                                expand=True,
                                                controls=[self.event_dropdown, self.date_range_btn]
                                            ),

                                            ft.Row(
                                                margin=ft.Margin(top=15),
                                                expand=True,
                                                controls=[
                                                    ft.Button(
                                                        content="Submit",
                                                        expand=True,
                                                        style=ft.ButtonStyle(
                                                            shape=ft.RoundedRectangleBorder(radius=10)
                                                        ),
                                                        on_click=self.submit_absence_request
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ),
                    ),
                ]
            )
        )

    def date_range_changed(self):
        start, end = self.date_range_picker.start_value, self.date_range_picker.end_value
        self.date_range_btn.content = f"{start.strftime(DATE_FORMAT)} - {end.strftime(DATE_FORMAT)}"

    def absence_duration_changed(self):
        self.absence_duration_radio_group: ft.RadioGroup
        match self.absence_duration_radio_group.value:
            case "event":
                self.event_dropdown.visible = True
                self.date_range_btn.visible = False
            case "time":
                self.event_dropdown.visible = False
                self.date_range_btn.visible = True
            case other:
                self.event_dropdown.visible = False
                self.date_range_btn.visible = False

    def submit_absence_request(self):
        student_name = self.student_name_ipt.value
        reason = self.reason_ipt.value
        absence_type = self.absence_type_radio_group.value
        absence_duration_type = self.absence_duration_radio_group.value
        event_id = self.event_dropdown.value
        duration_start = self.date_range_picker.start_value
        duration_end = self.date_range_picker.end_value

        print("##### ABSENCE REQUEST #####")
        print(f"Student Name: {student_name}")
        print(f"Reason: {reason}")
        print(f"Absence Type: {absence_type}")
        print(f"Absence Duration: {absence_duration_type}")
        print(event_id, duration_start, duration_end)
