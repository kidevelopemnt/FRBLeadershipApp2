import flet as ft


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

        pass

