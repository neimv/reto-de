
from fastapi import FastAPI, HTTPException
from peewee import fn
from pydantic import BaseModel
from typing import List

from models import (
    State, Company, Person, City, Phone, Deparment, PersonDeparment
)


app = FastAPI()


class PersonWS(BaseModel):
    first_name: str
    last_name: str
    company_name: str
    address: str
    city: str
    state: str
    codezip: str
    phone1: str
    phone2: str
    email: str
    department: List[str]


@app.get('/')
def root():
    return {'hello': 'ws'}


@app.get('/api/person/')
def all_persons():
    persons = (Phone.select(
            Person.id,
            Person.first_name,
            Person.last_name,
            Person.email,
            Company.name.alias('company_name'),
            Company.address,
            Company.codezip.alias('zip'),
            City.name.alias('city'),
            State.name.alias('state'),
            Deparment.name.alias('deparment'),
            Phone.person_id,
            fn.array_agg(Phone.phone_number).alias('phone_numbers')
        )
        .group_by(
            Phone.person_id, Person, Company, City, State, Deparment
        )
        .join(Person)
        .join(Company)
        .join(City)
        .join(State)
        .join(PersonDeparment, on=(Person.id == PersonDeparment.person_id))
        .join(Deparment, on=(PersonDeparment.deparment_id == Deparment.id))
        .where(Person.deleted != True)
        .order_by(Person.id)
        .dicts()
    )

    response_persons = [
        {k: v for k, v in person.items() if k != 'person_id'} 
        for person in list(persons)
    ]
    response_total = len(response_persons)

    return {
        'results': response_persons,
        'total': response_total
    }


@app.get('/api/person/{person_id}')
def get_person(person_id):
    person = (Phone.select(
            Person.id,
            Person.first_name,
            Person.last_name,
            Person.email,
            Company.name.alias('company_name'),
            Company.address,
            Company.codezip.alias('zip'),
            City.name.alias('city'),
            State.name.alias('state'),
            Deparment.name.alias('deparment'),
            Phone.person_id,
            fn.array_agg(Phone.phone_number).alias('phone_numbers')
        )
        .group_by(
            Phone.person_id, Person, Company, City, State, Deparment
        )
        .join(Person)
        .join(Company)
        .join(City)
        .join(State)
        .join(PersonDeparment, on=(Person.id == PersonDeparment.person_id))
        .join(Deparment, on=(PersonDeparment.deparment_id == Deparment.id))
        .where(Person.id == person_id, Person.deleted != True)
        .order_by(Person.id)
        .dicts()
    )
    response_person = list(person)

    try:
        response_person = response_person.pop(0)
        del response_person['person_id']
    except IndexError:
        raise HTTPException(status_code=404, detail="Person not found")

    return {
        'id': person_id,
        'result': response_person
    }


@app.post('/api/person/')
def create_person(person: PersonWS):
    state = person.state
    deparments_id = []

    if len(state) != 2:
        raise HTTPException(
            status_code=400, detail="State field is necessary size of 2"
        )
    
    if not state.isalpha():
        raise HTTPException(
            status_code=400, detail="State field is necessary only letters"
        )

    # save or get state
    state_model, created = State.get_or_create(name=person.state)
    # save or get city
    city, created = City.get_or_create(
        name=person.city.upper(), state_id=state_model
    )
    # save or get Company
    company, created = Company.get_or_create(
        name=person.company_name,
        address=person.address,
        codezip=person.codezip,
        city_id=city
    )
    # save or get person
    person_model, created = Person.get_or_create(
        first_name=person.first_name,
        last_name=person.last_name,
        email=person.email,
        deleted=False,
        company_id=company
    )
    # save or get department
    for dep in person.department:
        deparment, created = Deparment.get_or_create(
            name=dep
        )

        deparments_id.append(deparment)
    # save or get phone
    Phone.get_or_create(
        phone_number=person.phone1,
        person_id=person_model
    )
    Phone.get_or_create(
        phone_number=person.phone2,
        person_id=person_model
    )
    # save or get person_deparment
    for d in deparments_id:
        PersonDeparment.get_or_create(
            person_id=person_model,
            deparment_id=d
        )

    return {'id': person_model.id, 'detail': 'person created'}


@app.delete('/api/person/{person_id}')
def delete_person(person_id):
    person = Person.get_or_none(Person.id == person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    person.deleted = True
    person.save()

    return {
        'id': person_id,
        'result': 'Person deleted'
    }