import flet as ft

from db_system import Database
from models import User, AttendanceRecord, Tag
from settings import DT_FORMAT


class EventView(ft.Column):
    STATUSES = [
        "Not Recorded",
        "Present",
        "Absent",
        "Tardy",
        "Left Early"
    ]

    def __init__(self, page, user, event):
        self.app_page = page
        self.user = user
        self.event = event

        self.cards = []
        self.selected_tags = []

        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        self.build()

    def build(self):
        self.controls.clear()
        self.cards.clear()

        self.attendance_records = {
            record.user.id: record
            for record in AttendanceRecord.objects.filter(
                event=self.event
            )
        }

        self.controls.append(
            ft.Text(
                self.event.name,
                size=30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            )
        )

        self.controls.append(
            ft.Text(
                f"{self.event.start_dt.strftime(DT_FORMAT)} {self.event.end_dt.strftime(DT_FORMAT)}",
                size=30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            )
        )

        # Floating buttons
        self.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.FloatingActionButton(
                        icon=ft.Icons.CHECK,
                        # text="Mark All Present",
                        on_click=self.mark_all_present
                    ),

                    ft.FloatingActionButton(
                        icon=ft.Icons.CLOSE,
                        # text="Mark All Absent",
                        on_click=self.mark_all_absent
                    ),

                    ft.FloatingActionButton(
                        icon=ft.Icons.DELETE,
                        on_click=self.mark_all_not_recorded
                    )
                ]
            )
        )

        self.controls.append(
            self.tag_filter()
        )

        grid = ft.ResponsiveRow()

        people = User.objects.all()

        for user in people:
            card = self.user_card(user)
            grid.controls.append(card)

        self.controls.append(grid)

    def user_card(self, user):

        status = self.get_status(user)


        dropdown = ft.Dropdown(

            value=status,

            options=[

                ft.dropdown.Option(
                    s
                )

                for s in self.STATUSES

            ],

            width=160

        )

        dropdown.on_text_change = lambda e: self.change_status(user, e.control.value)

        card = ft.Container(
            col={
                "xs": 12,   # phones: 1
                "sm": 6,    # small: 2
                "md": 4,    # medium: 3
                "lg": 3,    # large: 4
                "xl": 2     # extra large: 6 (too many)
            },

            padding=10,

            content=ft.Card(
                bgcolor = self.status_color(status),

                content=ft.Container(
                    padding=15,
                    on_click=lambda e:
                        self.cycle_status(
                            user,
                            dropdown
                        ),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                user.name,
                                size=18,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Row(
                                wrap=True,
                                alignment= ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Chip(
                                        label=ft.Text(
                                            tag.name
                                        )
                                    )
                                    for tag in user.tags
                                ]
                            ),
                            ft.Divider(),
                            ft.Text(
                                status,
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),
                            dropdown
                        ]
                    )
                )
            )
        )

        self.cards.append(
            (user, card, dropdown, status)
        )

        return card

    def tag_filter(self):
        tags = Tag.objects.all()

        return ft.Row(
            wrap=True,
            controls=[
                ft.Chip(
                    label=ft.Text(tag.name),
                    selected=tag.id in self.selected_tags,
                    on_select=lambda e, t=tag:
                        self.toggle_tag(t, e.control.selected)
                )
                for tag in tags
            ]
        )

    def toggle_tag(self, tag, selected):
        if selected:
            if tag.id not in self.selected_tags:
                self.selected_tags.append(tag.id)
        else:
            if tag.id in self.selected_tags:
                self.selected_tags.remove(tag.id)

        self.build()
        self.update()

    def update_card(self, user, status):
        for card in self.cards:
            if card[0].id == user.id:
                card[2].value = status
                card[1].content.bgcolor = self.status_color(status)

                card[2].update()
                card[1].update()

                break

    def filtered_users(self):
        users = User.objects.all()

        if not self.selected_tags:
            return users

        filtered = []

        for user in users:

            # OR matching
            if any(
                    tag.id in self.selected_tags
                    for tag in user.tags
            ):
                filtered.append(user)

        return filtered

    def get_status(self, user):
        record = self.attendance_records.get(
            user.id
        )

        if record:
            return record.status

        return "Not Recorded"

    def cycle_status(self, user, dropdown):
        current = dropdown.value

        index = self.STATUSES.index(
            current
        )

        next_status = self.STATUSES[
            (index + 1)
            %
            len(self.STATUSES)
        ]

        dropdown.value = next_status

        self.change_status(
            user,
            next_status
        )

        dropdown.update()

    def change_status(self, user, status, refresh=True):
        record = self.attendance_records.get(user.id)

        if status == "Not Recorded":
            if record:
                record.delete()

            return

        if record:
            record.status = status

        else:
            record = AttendanceRecord(
                user=user,
                event=self.event,
                recorded_by=self.user,
                status=status
            )

        record.save()

        if refresh:
            self.update_card(user, status)

    def mark_all_present(self, e):
        self.mark_all(
            "Present"
        )


    def mark_all_absent(self, e):
        self.mark_all(
            "Absent"
        )

    def mark_all_not_recorded(self, e):
        self.mark_all("Not Recorded")

    def mark_all(self, status):
        if status == "Not Recorded":
            Database.execute(
                """
                DELETE FROM attendancerecord
                WHERE event=?
                """,
                (self.event.id,)
            )

            self.attendance_records.clear()

            for user, _, _, _ in self.cards:
                self.update_card(
                    user,
                    "Not Recorded"
                )

            return

        Database.begin()

        for user, _, _, _ in self.cards:
            self.change_status(
                user,
                status,
                refresh=False
            )

        Database.commit()

        for user, _, _, _ in self.cards:
            self.update_card(
                user,
                status
            )

    def status_color(self, status):
        colors = {
            "Present": "#C8E6C9",  # Pale green
            "Absent": "#FFCDD2",  # Pale red
            "Tardy": "#FFF9C4",  # Pale yellow
            "Left Early": "#FFE0B2",  # Pale orange
            "Not Recorded": "#EEEEEE"  # Light gray
        }

        return colors.get(
            status,
            "#EEEEEE"
        )