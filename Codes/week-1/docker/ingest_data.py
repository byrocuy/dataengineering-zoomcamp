from time import time
import os

import pandas as pd
import argparse
from sqlalchemy import create_engine

def main(params):
    username = params.username
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'data.csv'

    print('Downloading CSV....')
    os.system(f'wget {url} -O {csv_name}')
    print('Done.\n')

    print('\n==========================\n')
    
    print('Ingesting data....')

    # Connect to Postgre Database
    engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}')
    engine.connect()

    # Read data on chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Create SQL Scheme based on columns name
    head = next(df_iter).head(0)
    head.to_sql(name=table_name, con=engine, if_exists='replace')

    # iterate data over chunks
    for item in df_iter:
        t_start = time()
        
        item.tpep_pickup_datetime = pd.to_datetime(item.tpep_pickup_datetime)
        item.tpep_dropoff_datetime = pd.to_datetime(item.tpep_dropoff_datetime)

        item.to_sql(name=table_name, con=engine, if_exists='append')
        t_end = time()
            
        print('Inserted another cunk... time: %.3f seconds' % (t_end - t_start))

    print('\n==========================\n')
    print('Proces completed...')
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV to Postgre')

    parser.add_argument('--username', help='Insert postgreSQL username')
    parser.add_argument('--password', help='Insert postgreSQL password')
    parser.add_argument('--host', help='Insert postgreSQL host')
    parser.add_argument('--port', help='Insert postgreSQL port')
    parser.add_argument('--db', help='Insert postgreSQL db')
    parser.add_argument('--table_name', help='Name of the table where data will be ingested')
    parser.add_argument('--url', help='Insert CSV url')
    
    args = parser.parse_args()

    main(args)