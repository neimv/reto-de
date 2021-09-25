from pony.orm import *


db = Database()
db.bind(
    provider='postgres',
    user='neimv',
    password='12345678',
    host='localhost',
    database='neimv'
)


class Person(db.Entity):
    id = PrimaryKey(int, auto=True)
    first_name = Optional(str)
    last_name = Optional(str)
    email = Optional(str)
    deparments = Set('Deparment')
    phones = Set('Phone')
    company = Required('Company')


class Company(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    address = Optional(str)
    codezip = Optional(str)
    person = Optional(Person)
    state = Required('State')


class City(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    state = Required('State')


class State(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    city = Optional(City)
    company = Optional(Company)


class Phone(db.Entity):
    id = PrimaryKey(int, auto=True)
    phone_number = Optional(str)
    person = Required(Person)


class Deparment(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    persons = Set(Person)


db.generate_mapping(create_tables=True)
