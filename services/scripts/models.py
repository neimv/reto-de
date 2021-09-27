
import datetime
import os
import time

from peewee import (
    PostgresqlDatabase, CharField, Model, ForeignKeyField, BooleanField,
    DateTimeField, OperationalError
)

psql_db = PostgresqlDatabase(
    os.getenv('DB'),
    user=os.getenv('USER_DB'),
    password=os.getenv('PASSWORD_DB'),
    host=os.getenv('HOST_DB')
)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = psql_db


class State(BaseModel):
    name = CharField(max_length=2, unique=True)


class City(BaseModel):
    name = CharField(max_length=64, unique=True)

    state_id = ForeignKeyField(State)


class Company(BaseModel):
    name = CharField(max_length=64, unique=True)
    address = CharField(max_length=128)
    codezip = CharField(max_length=8)

    city_id = ForeignKeyField(City)


class Person(BaseModel):
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    email = CharField(max_length=64, unique=True)
    deleted = BooleanField(default=False)

    company_id = ForeignKeyField(Company)


class Phone(BaseModel):
    phone_number = CharField(max_length=16, unique=True)
    person_id = ForeignKeyField(Person)


class Deparment(BaseModel):
    name = CharField(max_length=32, unique=True)


class PersonDeparment(BaseModel):
    person_id = ForeignKeyField(Person)
    deparment_id = ForeignKeyField(Deparment)

    class Meta:
        indexes = (
            (('person_id', 'deparment_id'), True),
        )


class Errors(BaseModel):
    filename = CharField()
    error = CharField()
    date_error = DateTimeField(default=datetime.datetime.now)


def start_db(db):
    db.connect()
    db.create_tables(
        [
            Person, Company, City, State, Phone, Deparment, PersonDeparment,
            Errors
        ]
    )


if __name__ == '__main__':
    if os.getenv('START_DB'):
        for i in range(3):
            try:
                start_db(psql_db)
                break
            except OperationalError:
                time.sleep(10)
