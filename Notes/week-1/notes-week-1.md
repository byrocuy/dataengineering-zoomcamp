# 1. Conterization and Infrastructure as a Code

This is the notes for week 1 of the course [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp/). You can find the code, steps and some explanation for the week 1 maerials. At the end of the notes, you can find some [errors I encountered and the solutions](#some-errors-i-encountered-and-the-solutions) that maybe helps if you encounter the same errors.

Tools and environment used in my local machine are as follows:
- Windows 10
- Docker Desktop
- Command Prompt (CMD)
- Visual Studio Code
- Miniconda

# Table of Contents
  - [1.2. Docker and Docker-Compose](#12-docker-and-docker-compose)
    - [1.2.4 Dockerizing the Ingestion Script](#124-dockerizing-the-ingestion-script)
    - [1.2.5 Running Postgres and pgAdmin with Docker-Compose](#125-running-postgres-and-pgadmin-with-docker-compose)
    - [1.2.6. SQL Refresher](#126-sql-refresher)
  - [1.3. Terraform Basics](#13-terraform-basics)
    - [1.3.1. Terraform Primer](#131-terraform-primer)
    - [1.3.2. Terraform Basics (Walkthrough basic operations)](#132-terraform-basics-walkthrough-basic-operations)
    - [1.3.3. Terraform Variables](#133-terraform-variables)
  - [Some Errors I Encountered and the Solutions](#some-errors-i-encountered-and-the-solutions)


## 1.2. Docker and Docker-Compose
### 1.2.4 Dockerizing the Ingestion Script

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

### 1.2.5 Running Postgres and pgAdmin with Docker-Compose

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

### 1.2.6. SQL Refresher
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

## 1.3. Terraform Basics

First, setup Terraform and GCP SDK:
- Terraform [[here](https://developer.hashicorp.com/terraform/install)]
- GCP SDK [[here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/01-docker-terraform/1_terraform_gcp/2_gcp_overview.md#initial-setup)]

### 1.3.1. Terraform Primer
▶️ [[Video Link](https://www.youtube.com/watch?v=s2bOYDCKl_M&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11)]

Terraform is an **infrastructure as** code tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle.

Why use Terraform?
- simplicity in keeping track of infrastructure
- Easier collaboration
- Reproducibility
- Ensure resources are removed

Terraform is not:
- does not manage and update code on infrastructure
- does not give you the ability to change immutable resources
- not used to manage resources not defined in your terraform files

Key Terraform commands:
- `init` - get me the providers 
- `plan`
- `apply`- do the thing in terraform
- `destroy` - destruct everything defined in terraform

### 1.3.2. Terraform Basics (Walkthrough basic operations)
▶️ [[Video Link](https://www.youtube.com/watch?v=Y2ux7gq3Z0o&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=12)]

Setting up service account in Google Cloud Platform (GCP):
1. Go to the [GCP console](https://console.cloud.google.com/) and create new project
2. Head to IAM & Admin > Service Accounts
3. Create a new service account, give it a name (e.g. `terraform-runner`) > Continue
4. Give it a role as `Storage Admin`, add another role as `BigQuery Admin`, lastly, add `Compute Admin` role > Continue  
**note**: _In real world, you want to limit these permissions._    
for storage creator, we only need ability to create buckets and destroy. for bigquery, we only need ability to create and destroy datasets and tables.
5. Skip and click Done. _If you need to create additional role, just go to IAM menu and go to your service account and add additional role._
6. In the service accounts for the project, click three dots menu at the service account just created, and click manage keys.
7. Create new keys and choose json. A json file will be downloaded to your computer, this is the key file that will be used in terraform. Keep it in somewhere safe directory.
8. Use that json file to authenticate GCP. You can see the instructions via GCP installation instruction above.

Setting up Terraform in VSCode environment:
- Install Terraform extension in VSCode, you can use the one from HashiCorp.

First, we are going to init Terraform. Create a new file `main.tf` and put the following code:

```hcl
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  provider "google" {
  project     = "my-project-id" # put your GCP project id here
  region      = "us-central1"
  zone        = "us-central1-c"
}
}
```

Then run `terraform init` in the terminal same directory as the `main.tf` file. This will download the provider plugin for Google Cloud Platform and will generate a bunch of new files and folders. Make sure to add Terraform .gitignore template to your `.gitignore` file. For reference, see template [here](https://github.com/github/gitignore/blob/main/Terraform.gitignore)

Next, we are going to create Google Bucket Storage via Terraform. We will see how powerful Terraform is in managing infrastructure. 

Edit `main.tf' file and add the following code at the end of the file:

```hcl
resource "google_storage_bucket" "demo-bucket" {
  name          = "demo-terraform-bucket" # unique name 
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

run `terraform plan` and then `terraform apply` commands in the terminal. This will create a bucket in your GCP project. You can check it in the GCP console.

Now we will destroy the bucket we just created. Simply run `terraform destroy` in the terminal. This will destroy the bucket in your GCP project.

### 1.3.3. Terraform Variables

▶️ [[video link](https://www.youtube.com/watch?v=PBi0hHjLftk&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=14)]

Now we will leverage developing Terraform with variables. With Terraform variables, we don't need to hard code the values in the Terraform file everytime we want to create a new resource. We can use variables to make the code more reusable and easier to maintain. 

For example, instead of hard coding the location of the bucket (e.g. `US`), we can use a variable to define the location, so that if we want to change the location, we only need to change the value of the variable, once.

In the following tutorial, we will create BigQuery Table using Terraform and set it up with variables. 

In the `main.tf` file, add the following code at the end of the file:

```hcl
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = 'demo_dataset'
  location   = 'US'
}
```

Full code for `main.tf` file:

```hcl
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  project     = "dataengzoocamp-375210" # put your GCP project id here
  region      = "us-central1"
  zone        = "us-central1-c"
}

resource "google_storage_bucket" "demo-bucket" {
  name          = "demo-terraform-bucket"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "US"
}
```

We see that in the above code, we still hardcode some of the values, like the project id, location, region, etc. We can use variables to make the code more reusable and easier to maintain.

First, create a new file `variables.tf` and add variable for every value that we want to make it reusable. For example, in this project we will create variables for project id, region, zone, bucket_name, and bigquery_dataset_id. The code is as follows:

```hcl
variable "project_id" {
  description = "The project id"
  default = "dataengzoocamp-375210" # Replace with your GCP project id
}

variable "region" {
  description = "The region"
  default = "us-central1"
}

variable "zone" {
  description = "The zone"
  default = "us-central1-c"
}

variable "location" {
  description = "The location for the bucket"
  default = "US"
}

variable "bucket_name" {
  description = "The bucket name"
  default = "demo-terraform-bucket"
}

variable "bq_dataset_id" {
  description = "The bigquery dataset id"
  default = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "The storage class for the bucket"
  default = "STANDARD"
}
```

You can also add your gcp credentials via terraform variables instead of setting it up in the terminal variable, by adding the following code in the `variables.tf` file:

```hcl
variable "credentials" {
  description = "The path to the GCP credentials file"
  default = "path/to/your/credentials.json"
}
```

Then, in the `main.tf` file, replace the hardcoded values with the variables we have created. Example as follows:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_id
  location   = var.location
}
```

After that, run `terraform plan` and `terraform apply` commands in the terminal. This will create a bucket and bigquery dataset in your GCP project. You can check it in the GCP console that a bucket and bigquery table has been created.

Run `terraform destroy` to destroy the resources we just created. Check in the GCP console that the resources have been destroyed.

That's it for the week 1 notes. Thank you for reading ^^

# Some Errors I Encountered and the Solutions

#### `OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: Connection refused (0x0000274D/10061)`

Solution: Most likely the port is used in another process. 
some troubleshooting maybe will help:
1. Try login to the database using `pgcli` in your CLI: `pgcli -h localhost -p 5432 -U root -d ny_taxi` if it occurs `connection failed: password authentication failed for user "root"` then most likely the port is used in another process.
2. Try kill the process that uses the port. Check the process that uses the port using `netstat -ano | findstr :5432` then kill the process using `taskkill /PID <PID> /F` where `<PID>` is the process ID. If access denied, run the CMD as administrator and try kill it again
3. Try login again to the database using `pgcli`. if it's success then run the script again.