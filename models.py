from datetime import datetime

from db_system import Model, Manager
from settings import DT_FORMAT


class Tag(Model):
    fields = {
        "name": "",
        "color": "#000000",
    }


class User(Model):
    fields = {
        "username": None,
        "password": None,
        "name": "",
        "tags": [Tag],              # List[Tag]   0 means ALL
        "managing_tags": [Tag],     # List[Tag]   0 means ALL
        "active": True,
    }


class Event(Model):
    CATEGORY_REHEARSAL = "Rehearsal"
    CATEGORY_SECTIONAL = "Sectional"
    CATEGORY_PERFORMANCE = "Performance"
    CATEGORY_OTHER = "Other"

    CATEGORY_CHOICES = [
        CATEGORY_REHEARSAL,
        CATEGORY_SECTIONAL,
        CATEGORY_PERFORMANCE,
        CATEGORY_OTHER,
    ]

    fields = {
        "name": "",
        "category": CATEGORY_REHEARSAL,
        "location": "",
        "_start_dt": None,       # datetime
        "_end_dt": None,         # datetime
        "notes": "",
        "created_by": User,      # User
        "tags": [Tag],              # List[Tag]   0 means ALL
        "mandatory": True,
        "attendance_locked": False,
    }

    @property
    def start_dt(self):
        return datetime.strptime(self._start_dt, DT_FORMAT)

    @start_dt.setter
    def start_dt(self, value):
        self._start_dt = value

    @property
    def end_dt(self):
        return datetime.strptime(self._end_dt, DT_FORMAT)

    @end_dt.setter
    def end_dt(self, value):
        self._end_dt = value


class AttendanceRecord(Model):
    STATUS_PRESENT = "Present"
    STATUS_TARDY = "Tardy"
    STATUS_ABSENT = "Absent"
    STATUS_LEFT_EARLY = "Left Early"

    STATUS_CHOICES = [
        STATUS_PRESENT,
        STATUS_TARDY,
        STATUS_ABSENT,
        STATUS_LEFT_EARLY,
    ]

    fields = {
        "user": User,              # User
        "event": Event,               # Event
        "recorded_by": User,         # User
        "recorded_at": None,         # datetime
        "status": STATUS_PRESENT,
        "notes": "",
        "excused": False,
        "locked": False,
    }

    def save(self):
        if self.recorded_at is None:
            self.recorded_at = datetime.now()
        super().save()


class AbsenceRequest(Model):
    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_DENIED = "Denied"

    STATUS_CHOICES = [
        STATUS_PENDING,
        STATUS_ACCEPTED,
        STATUS_DENIED,
    ]

    fields = {
        "user": User,              # User

        # Either this...
        "event": Event,               # Event

        # ...or these
        "start_dt": None,            # datetime
        "end_dt": None,              # datetime

        "recorded_by": User,         # User
        "recorded_at": None,         # datetime

        "absence_type": "",
        "notes": "",

        "reviewed_by": User,         # User
        "reviewed_at": None,         # datetime

        "approval_status": STATUS_PENDING,
    }

    def save(self):
        """
        Validation:
        - Either an Event OR a Start/End datetime range may be supplied.
        - Not both.
        - Not neither.
        """

        has_event = self.event is not None
        has_range = self.start_dt is not None or self.end_dt is not None

        if has_event and has_range:
            raise ValueError(
                "AbsenceRequest cannot have both an event and a datetime range."
            )

        if not has_event and not has_range:
            raise ValueError(
                "AbsenceRequest requires either an event or a datetime range."
            )

        if has_range:
            if self.start_dt is None or self.end_dt is None:
                raise ValueError(
                    "Both start_dt and end_dt are required for a datetime range."
                )

            if self.end_dt <= self.start_dt:
                raise ValueError(
                    "end_dt must be after start_dt."
                )

        if self.recorded_at is None:
            self.recorded_at = datetime.now()

        super().save()

Tag.objects = Manager(Tag)
User.objects = Manager(User)
Event.objects = Manager(Event)
AttendanceRecord.objects = Manager(AttendanceRecord)
AbsenceRequest.objects = Manager(AbsenceRequest)

Tag.generate_table()
User.generate_table()
Event.generate_table()
AttendanceRecord.generate_table()
AbsenceRequest.generate_table()
