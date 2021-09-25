
from peewee import (
    PostgresqlDatabase, CharField, Model, ForeignKeyField
)

psql_db = PostgresqlDatabase(
    'neimv',
    user='neimv',
    password='12345678',
    host='localhost'
)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = psql_db


class State(BaseModel):
    name = CharField(max_length=2, unique=True)


class Company(BaseModel):
    name = CharField(max_length=64, unique=True)
    address = CharField(max_length=128)
    codezip = CharField(max_length=8)

    state = ForeignKeyField(State)


class Person(BaseModel):
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    email = CharField(max_length=64, unique=True)

    company = ForeignKeyField(Company)


class City(BaseModel):
    name = CharField(max_length=64, unique=True)

    state = ForeignKeyField(State)


class Phone(BaseModel):
    phone_number = CharField(max_length=16, unique=True)
    person = ForeignKeyField(Person)


class Deparment(BaseModel):
    name = CharField(max_length=32, unique=True)


class PersonDeparment(BaseModel):
    person = ForeignKeyField(Person)
    deparment = ForeignKeyField(Deparment)

    class Meta:
        indexes = (
            (('person', 'deparment'), True),
        )


def start_db(db):
    db.connect()
    db.create_tables(
        [Person, Company, City, State, Phone, Deparment, PersonDeparment]
    )


start_db(psql_db)
