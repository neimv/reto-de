import logging
import mimetypes

import coloredlogs
import pandas as pd

from models import (
    State, Company, Person, City, Phone, Deparment, PersonDeparment
)


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


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
        self.df = self.df[self.fields]

    def transform(self):
        logger.info(self.df.head())
        list_grouped = set(self.fields) - set(['department'])
        grouped = self.df.groupby(list(list_grouped))['department'].transform(
            lambda x: ','.join(x)
        ).to_frame()
        grouped["id"] = grouped.index + 1

        df = self.df[list_grouped]
        df['id'] = df.index + 1

        logger.info(grouped)
        logger.info(df)

        df_work = pd.merge(df, grouped, on='id')
        del df_work['id']
        df_work.drop_duplicates(inplace=True)

        df_work['phones'] = df_work[['phone1', 'phone2']].apply(
            lambda x: [x[0], x[1]], axis=1
        )
        df_work['department'] = df_work['department'].apply(
            lambda x: x.split(',')
        )
        logger.info(df_work)

        self.df = df_work.copy()

    def load(self):
        logger.warning(self.df)
        # save or get state
        # save or get city
        # save or get Company
        # save or get person
        # save or get department


if __name__ == '__main__':
    etl = ETL('Sample.csv')
    etl.main()
