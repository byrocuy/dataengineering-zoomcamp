# 1.2. Docker and Docker-Compose

Table of Contents:
- [1.2.1. Introduction to Docker](#121-introduction-to-docker)
- [1.2.2. Running Postgres with Docker](#122-running-postgres-with-docker)
- [1.2.3. Running Python Script to Ingest Data](#123-running-python-script-to-ingest-data)
- [1.2.4 Dockerizing the Ingestion Script](#124-dockerizing-the-ingestion-script)
- [1.2.5 Running Postgres and pgAdmin with Docker-Compose](#125-running-postgres-and-pgadmin-with-docker-compose)
- [1.2.6. SQL Refresher](#126-sql-refresher)

## 1.2.4 Dockerizing the Ingestion Script

Full code for the ingestion script:
```python

import os
import argparse
from time import time

import pandas as pd
from sqlalchemy import create_engine

def main(params):
    username = params.username
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    file_path = params.file_path

    engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}')
    engine.connect()

    df_iter = pd.read_csv(file_path, iterator=True, chunksize=100000)

    head = next(df_iter).head(0)
    head.to_sql(table_name, con=engine, if_exists='replace')

    for item in df_iter:
        t_start = time()

        item.tpep_pickup_datetime = pd.to_datetime(item.tpep_pickup_datetime)
        item.tpep_dropoff_datetime = pd.to_datetime(item.tpep_dropoff_datetime)

        item.to_sql(table_name, con=engine, if_exists='append')

        t_end = time()

        print('Inserted another chunk, took %.3f second' % (t_end - t_start))

    print('Finished inserting all chunks')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest data into Postgres SQL')

    parser.add_argument('--username', required=True, help='Username for the database', type=str)
    parser.add_argument('--password', required=True, help='Password for the database', type=str)
    parser.add_argument('--host', required=True, help='Host for the database')
    parser.add_argument('--port', required=True, help='Port for the database', type=int)
    parser.add_argument('--db', required=True, help='Database name for the database', type=str)
    parser.add_argument('--table_name', required=True, help='Table name for the database', type=str)
    parser.add_argument('--file', required=True, help='File location of the CSV', type=str)

    args = parser.parse_args()

    main(args)
```
Now we run the script `ingest_data.py`:

```bash
python ingest_data.py ^
--username="root" ^
--password="root" ^
--host="localhost" ^
--port=5432 ^
--db="ny_taxi" ^
--table_name="yellow_taxi_data" ^
--file_path="D:\labs\zoomcamp\week-1\docker\yellow_tripdata_2021-01.csv"

# or you can use this (it's the same)

python ingest_data.py --username root --password root --host localhost --port 5432 --db ny_taxi --table_name yellow_taxi_data --file_path D:\labs\zoomcamp\week-1\docker\yellow_tripdata_2021-01.csv
```

Now we will create a Dockerfile to containerize the script. Don't forget to drop the table in the database to see this effect. 

The Dockerfile is as follows:

```Dockerfile

FROM python:3.9

RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY ingest_data.py ingest_data.py

# I have downloaded the CSV file and this will put the file in the container
COPY yellow_tripdata_2021-01.csv yellow_tripdata_2021-01.csv

ENTRYPOINT ["python", "ingest_data.py"]

```
Then run the following commands to build and run the container:

First, build the container:
```bash
docker build -t taxi_ingest:v001 .
```

Then run the container:   

```bash
# Run the container
docker run -it ^
     --network=pg-network ^
     taxi_ingest:v001 ^
        --username="root" ^
        --password="root" ^
        --host="pg-database" ^
        --port=5432 ^
        --db="ny_taxi" ^
        --table_name="yellow_taxi_data" ^
        --file_path="yellow_tripdata_2021-01.csv"

```

## 1.2.5 Running Postgres and pgAdmin with Docker-Compose

▶️ [[Video Link](https://www.youtube.com/watch?v=hKI6PkPhpa0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=12)]

We will create `docker-compose.yml` file to run Postgres and pgAdmin. The configuration is as follows:

```yml
services:
  pgdatabase:
    image: postgres:13
    environment:
        - POSTGRES_USER=root
        - POSTGRES_PASSWORD=root
        - POSTGRES_DB=ny_taxi
    volumes:
        - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
        - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
        - PGADMIN_DEFAULT_EMAIL=admin@admin.com
        - PGADMIN_DEFAULT_PASSWORD=admin
    volumes:
        - "pgadmin_conn_data:/var/lib/pgadmin:rw"
    ports:
        - "8080:80"
volumes:
    pgadmin_conn_data:
```

Stop the running container pgAdmin and Postgress if any. You can stop the running container either by exiting the container with `CTRL+C` in CLI or by running `docker stop <container_id>`.

You can check the container id by running `docker ps` to see current running containers.

Go to http://localhost:8080, enter the credentials and create a new server. Enter the following details:
Tab General: Name: Local Docker
Tab Connection:
- Host name/address: `pgdatabase`
- Port: `5432`
- Username: `root`
- Password: `root`

Then click Save.

Check the database `ny_taxi` and the table `yellow_taxi_data` in the pgAdmin.

Don't forget to stop the running containers by running `docker-compose down` in the CLI.

## 1.2.6. SQL Refresher
▶️ [[Video Link](https://www.youtube.com/watch?v=QEcps_iskgg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=10)]

joining yellow taxi data table with the zones lookup table

```sql
/* INNER JOIN*/

SELECT 
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' / ', zpu."Zone") as "PU_Location",
    CONCAT(zdo."Borough", ' / ', zdo."Zone") as "DO_Location"
FROM 
    yellow_taxi_data t,
    zones zpu,
    zones zdo
WHERE
    t."PULocationID" = zpu."LocationID" AND
    t."DOLocationID" = zdo."LocationID"
LIMIT 10
```

Check if there is zone in `yellow_taxi_data` that is not in `zones` table

```sql
SELECT 
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    "PULocationID",
    "DOLocationID"
FROM 
    yellow_taxi_data t
WHERE
    "PULocationID" NOT IN (SELECT "LocationID" FROM zones)
LIMIT 10
```
output: there is None

```sql
SELECT
    CAST(tpep_dropoff_datetime AS DATE) as "date",
    "DOLocationID",
    COUNT(1) as "count",
    MAX(total_amount),
    MAX(passenger_count)
FROM
    yellow_taxi_data t
GROUP BY
    1, 2
ORDER BY
    "count" DESC
```

<div align="center">

### [Home](README.md) | [1.3 Terraform Basics >>](./3-terraform-basics.md)

</div>