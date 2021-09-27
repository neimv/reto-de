import logging

import coloredlogs
import pandas as pd

from models import (
    State, Company, Person, City, Phone, Deparment, PersonDeparment, Errors
)


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)


class ETL:
    def __init__(self, file):
        self.file = file
        self.df = None
        self.fields = [
            'first_name',
            'last_name',
            'company_name',
            'address',
            'city',
            'state',
            'zip',
            'phone1',
            'phone2',
            'email',
            'department'
        ]
        self.readers = [
            pd.read_csv, pd.read_json, pd.read_html, pd.read_xml,
            pd.read_excel, pd.read_parquet
        ]

    def main(self):
        self.extract()
        self.transform()
        self.load()

    def extract(self):
        for read in self.readers:
            try:
                self.df = read(self.file)
            except FileNotFoundError:
                raise Exception("File csv does not exists")
            except Exception:
                pass

        # Check if get all fields
        try:
            self.df = self.df[self.fields]
        except Exception as e:
            raise Exception("Files csv not contains all fields")

    def transform(self):
        logger.debug(self.df.head())
        # Check errors in dataframe
        ## first check nones
        mask = pd.isnull(self.df).stack()
        null_values = mask.loc[mask].index.tolist()

        if null_values:
            for nulls in null_values:
                Errors.create(
                    filename=self.file.split('/')[-1],
                    error=f'Column {nulls[1]} is null in Index: {nulls[0]}'
                )

                try:
                    self.df.drop(nulls[0], inplace=True)
                except KeyError:
                    logger.debug('Key deleted')

                logger.debug(self.df)

        self.df['state_size'] = self.df['state'].apply(len)
        logger.debug(self.df['state_size'])

        df_errors = self.df[self.df['state_size'] != 2]
        logger.debug(df_errors)

        if df_errors.empty is False:
            for index, _ in df_errors.iterrows():
                logger.debug(index)
                Errors.create(
                    filename=self.file.split('/')[-1],
                    error=f'State Index: {index} has length is not 2'
                )

        del self.df['state_size']

        list_grouped = set(self.fields) - set(['department'])
        grouped = self.df.groupby(list(list_grouped))['department'].transform(
            lambda x: ','.join(x)
        ).to_frame()
        grouped["id"] = grouped.index + 1

        df = self.df[list_grouped]
        df['id'] = df.index + 1

        logger.debug(grouped)
        logger.debug(df)

        df_work = pd.merge(df, grouped, on='id')
        del df_work['id']
        df_work.drop_duplicates(inplace=True)

        df_work['phones'] = df_work[['phone1', 'phone2']].apply(
            lambda x: [x[0], x[1]], axis=1
        )
        df_work['department'] = df_work['department'].apply(
            lambda x: x.split(',')
        )
        logger.debug(df_work)

        self.df = df_work.copy()

    def load(self):
        logger.debug(self.df)
        # save or get state
        logger.info('save STATE')
        self.df['state_model'] = self.df['state'].apply(
            self.__get_save_state
        )
        # save or get city
        logger.info('save CITY')
        self.df['city_model'] = self.df[['city', 'state_model']].apply(
            self.__get_save_city, axis=1
        )
        # save or get Company
        logger.info('save COMPANY')
        self.df['company_id'] = self.df[
            ['company_name', 'address', 'zip', 'city_model']
        ].apply(self.__get_save_company, axis=1)
        # save or get person
        logger.info('save PERSON')
        self.df['person_id'] = self.df[
            ['first_name', 'last_name', 'email', 'company_id']
        ].apply(self.__get_save_person, axis=1)
        # save or get department
        logger.info('save DEPARMENT')
        self.df['deparments_id'] = self.df['department'].apply(
                self.__get_save_deparments
        )
        # save or get phone
        logger.info('save PHONES')
        self.df['phones_id'] = self.df[
            ['phones', 'person_id']
        ].apply(self.__get_save_phones, axis=1)
        logger.debug(self.df.columns.values)
        # save or get person_deparment
        logger.info('save PERSON DEPARMENT')
        self.df['per_dep'] = self.df[
            ['person_id', 'deparments_id']
        ].apply(self.__get_save_person_company, axis=1)
        logger.warning(self.df)

    def __get_save_state(self, state_name):
        state = State.get_or_none(State.name == state_name)

        if state is None:
            state = State.create(name=state_name)

        return state

    def __get_save_city(self, values):
        logger.debug(values)
        city = City.get_or_none(
            City.name == values.city, City.state_id == values.state_model
        )

        if city is None:
            city = City.create(name=values.city, state_id=values.state_model)

        return city

    def __get_save_company(self, values):
        logger.debug(values)
        company = Company.get_or_none(
            Company.name == values.company_name,
            Company.address == values.address,
            Company.codezip == values.zip,
            Company.city_id == values.city_model
        )

        if company is None:
            company = Company.create(
                name=values.company_name,
                address=values.address,
                codezip=values.zip,
                city_id=values.city_model
            )

        return company

    def __get_save_person(self, values):
        logger.debug(values)
        person = Person.get_or_none(
            Person.first_name == values.first_name,
            Person.last_name == values.last_name,
            Person.email == values.email,
            Person.company_id == values.company_id
        )

        if person is None:
            person = Person.create(
                first_name=values.first_name,
                last_name=values.last_name,
                email=values.email,
                delete=False,
                company_id=values.company_id
            )

        return person

    def __get_save_deparments(self, deparments_name):
        deparments_id = []

        for deparment in deparments_name:
            dep = Deparment.get_or_none(Deparment.name == deparment)

            if dep is None:
                dep = Deparment.create(name=deparment)

            deparments_id.append(dep)

        return deparments_id

    def __get_save_phones(self, values):
        phones_id = []
        phones = values.phones

        for phone_ in phones:
            phone = Phone.get_or_none(
                Phone.phone_number == phone_,
                Phone.person_id == values.person_id
            )

            if phone is None:
                phone = Phone.create(
                    phone_number=phone_, person_id=values.person_id
                )
            
            phones_id.append(phone)

        return phones_id

    def __get_save_person_company(self, values):
        per_deps = []
        departments = values.deparments_id

        for deparment in departments:
            per_dep = PersonDeparment.get_or_none(
                PersonDeparment.person_id == values.person_id,
                PersonDeparment.deparment_id == deparment
            )

            if per_dep is None:
                per_dep = PersonDeparment.create(
                    person_id=values.person_id,
                    deparment_id=deparment
                )

            per_deps.append(per_dep)

        return per_deps


if __name__ == '__main__':
    etl = ETL('Sample.csv')
    etl.main()
