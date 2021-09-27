# reto-de
reto of data engineer


## How to run

to run project execute:

1. execute `docker-compose up init` to start database
2. to run ws: `docker-compose up`

this project contains:

- two web service:
    - localhost:8000:
        - get `/api/person` to get all persons
        - get `/api/person/{id}` to retrieve one person
        - post `/api/person` to create new person, fields required has: ```
        {
            "first_name": "neimv",
            "last_name": "zatara",
            "company_name": "sintrafico",
            "address": "polanquito",
            "city": "CDMX",
            "state": "CD",
            "codezip": "54100",
            "phone1": "66677666121",
            "phone2": "66677666122",
            "email": "neimv.zatara@gmail.com",
            "department": ["noprueba"]
        } ```
        - delete `/api/person/{id}` to delete user, this is a logic delete
    - localhost:8001:
        - post `/submit_document/`, to submit file as Sample
