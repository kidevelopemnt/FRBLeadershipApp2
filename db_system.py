import os
import json
import sqlite3
import uuid
from datetime import datetime


# DATABASE = "D:\\Coding\\FRBLeadershipApp\\database.db"
DATABASE = "C:\\Users\\mike\\OneDrive\\Email attachments\\Desktop\\Braden\\Coding\\FRBLeadershipApp2\\database.db"


class Database:
    connection = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )

    in_transaction = False

    connection.row_factory = sqlite3.Row

    @classmethod
    def execute(cls, query, params=(), commit=True):
        cursor = cls.connection.cursor()
        cursor.execute(query, params)

        if commit:
            cls.connection.commit()

        return cursor

    @classmethod
    def fetchall(cls, query, params=()):
        cursor = cls.execute(query, params)
        return cursor.fetchall()

    @classmethod
    def fetchone(cls, query, params=()):
        cursor = cls.execute(query, params)
        return cursor.fetchone()

    @classmethod
    def begin(cls):
        cls.in_transaction = True
        cls.connection.execute("BEGIN TRANSACTION")

    @classmethod
    def commit(cls):
        cls.in_transaction = False
        cls.connection.commit()


class Model:
    fields = {}
    table_name = None

    _list_fields = {}  # key: References

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)

        for field, default in self.fields.items():

            # Many-to-many
            if isinstance(default, list) and len(default) == 1 and issubclass(default[0], Model):

                reference = default[0]

                value = kwargs.get(field, [])

                if isinstance(value, str):
                    value = self._load_many_to_many(
                        reference,
                        value
                    )

                setattr(
                    self,
                    field,
                    value
                )

                continue

            # Foreign key
            if isinstance(default, type) and issubclass(default, Model):
                value = kwargs.get(field)

                if value is not None and value != "" and not isinstance(value, Model):
                    print(default, value)
                    value = default.objects.get(
                        id=value
                    )

                setattr(
                    self,
                    field,
                    value
                )

                continue

            # Normal field
            setattr(
                self,
                field,
                kwargs.get(field, default)
            )

    def _load_many_to_many(
            self,
            model,
            value
    ):

        if not value:
            return []

        ids = value.split(",")

        if "0" in ids and len(ids) == 1:
            # 0 represents ALL
            ids = [obj.id for obj in model.objects.all()]

        return [
            model.objects.get(id=id)
            for id in ids
        ]


    def save(self):

        fields = list(self.fields.keys())

        values = [
            self._serialize(
                getattr(self, field)
            )
            for field in fields
        ]

        values.insert(0, self.id)


        columns = ", ".join(
            ["id"] + fields
        )

        placeholders = ", ".join(
            ["?"] * len(values)
        )


        update = ", ".join(
            [
                f"{field}=excluded.{field}"
                for field in fields
            ]
        )


        query = f"""
        INSERT INTO {self.table_name}
        ({columns})
        VALUES ({placeholders})

        ON CONFLICT(id)
        DO UPDATE SET
        {update}
        """

        Database.execute(
            query,
            values,
            commit=not Database.in_transaction
        )

    @classmethod
    def generate_table(cls):
        if not cls.table_name:
            cls.table_name = cls.__name__.lower()

        columns = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT"
        ]

        for field, default in cls.fields.items():
            if type(default) is list:
                cls._list_fields[field] = None

            columns.append(
                f"{field} TEXT"
            )

        query = f"""
            CREATE TABLE IF NOT EXISTS
            {cls.table_name}
            (
                {", ".join(columns)}
            )
            """

        Database.execute(query)


    def delete(self):

        Database.execute(
            f"""
            DELETE FROM {self.table_name}
            WHERE id=?
            """,
            (self.id,)
        )

    def _serialize(self, value):

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Model):
            return str(value.id)

        if isinstance(value, list):
            return ",".join(
                [
                    str(item.id)
                    for item in value
                ]
            )

        if type(value) is bool:
            value = int(value)

        elif value is None:
            value = ""

        return str(value)


    @classmethod
    def _deserialize(cls, value):
        return value



class Manager:


    def __init__(self, model):
        self.model = model

    def create(self, **kwargs):

        obj = self.model(**kwargs)
        obj.save()

        return obj

    def all(self):

        rows = Database.fetchall(
            f"""
            SELECT *
            FROM {self.model.table_name}
            """
        )

        return [
            self.model(**dict(row))
            for row in rows
        ]



    def filter(self, **kwargs):

        conditions = []
        values = []


        for key, value in kwargs.items():

            conditions.append(
                f"{key}=?"
            )

            values.append(
                self.model()._serialize(value)
            )


        query = f"""
        SELECT *
        FROM {self.model.table_name}
        """


        if conditions:

            query += " WHERE "
            query += " AND ".join(
                conditions
            )


        rows = Database.fetchall(
            query,
            values
        )


        return [
            self.model(**dict(row))
            for row in rows
        ]



    def get(self, **kwargs):

        results = self.filter(
            **kwargs
        )

        if len(results) == 0:
            raise Exception(
                "Object does not exist"
            )

        if len(results) > 1:
            raise Exception(
                "Multiple objects returned"
            )

        return results[0]



    def get_or_create(
        self,
        defaults=None,
        **kwargs
    ):

        try:
            return self.get(**kwargs), False

        except:

            data = kwargs.copy()

            if defaults:
                data.update(defaults)

            return self.create(**data), True