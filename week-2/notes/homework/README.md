# Module 2 Homework

Dataset for this homework is the [green taxi dataset](https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download)

## Instruction
- Create a new pipeline, call it `green_taxi_etl`
- Add a data loader block and use Pandas to read data for the final quarter of 2020 (months 10, 11, 12).
    - You can use the same datatypes and date parsing methods shown in the course.
    - BONUS: load the final three months using a for loop and `pd.concat`
- Add a transformer block and perform the following:
    - Remove rows where the passenger count is equal to 0 and the trip distance is equal to zero.
    - Create a new column lpep_pickup_date by converting lpep_pickup_datetime to a date.
    - Rename columns in Camel Case to Snake Case, e.g. `VendorID` to `vendor_id`.
    - Add three assertions:
        - `vendor_id` is one of the existing values in the column (currently)
        - `passenger_count` is greater than 0
        - `trip_distance` is greater than 0
- Using a Postgres data exporter (SQL or Python), write the dataset to a table called `green_taxi` in a schema `mage`. Replace the table if it already exists.
- Write your data as Parquet files to a bucket in GCP, partioned by `lpep_pickup_date`. Use the `pyarrow` library!
- Schedule your pipeline to run daily at 5AM UTC.

## Solutions
From the instruction, we can break down the tasks into the following sections:
1. Data loading: using data loader block to load the data for the final quarter of 2020 from the repository
2. Data transforming: using data transformer block to transform the data to the appropriate format
3. Data exporting: export the data to Postgres and GCS

### Data Loading

Here are the steps how I approach to load the data: 
- We need to load the data from the repository only for the final quarter of 2020, e.g. month 10, 11, and 12. 
- By inspecting the repository, we see that the data is stored for each month in a gzip compression. 
- We will loop through the months and load the data directly from the URLs using pandas `pd.read()`. 
    The URL format is `https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-{month}.csv.gz`, where `{month}` is the 10, 11, and 12.   
    example: `https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-10.csv.gz`
- Concat each loaded dataframe into a single dataframe using `pd.concat()`
  
The code:
```python
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd

@data_loader
def load_data(*args, **kwargs):
    taxi_dtypes = {
        'VendorID': float,
        'store_and_fwd_flag': str,
        'RatecodeID': pd.Int64Dtype(),
        'PULocationID': pd.Int64Dtype(),
        'DOLocationID': pd.Int64Dtype(),
        'passenger_count': pd.Int64Dtype(),
        'trip_distance': float,
        'fare_amount': float,
        'extra': float,
        'mta_tax': float,
        'tip_amount': float,
        'tolls_amount': float,
        'ehail_fee': float,
        'improvement_surcharge': float,
        'total_amount': float,
        'payment_type': float,
        'trip_type': float,
        'congestion_surcharge': float
    }

    # Parse columns as datetime data type
    parse_dates = ["lpep_pickup_datetime", "lpep_dropoff_datetime"]
    
    # final quarter month
    months = [10, 11, 12]
    
    # Initialize empty df for concatenating all df months
    df = pd.DataFrame()

    for month in months:
        url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-{month}.csv.gz"
        df_per_month = pd.read_csv(url, compression="gzip", dtype=taxi_dtypes, parse_dates=parse_dates)
        df = pd.concat([df, df_per_month])

    return df


@test
def test_output(output, *args) -> None:

    assert output is not None, 'The output is undefined
```

### Data Transforming
For the transforming steps, the instruction is already clear on what to do. 
- We need to remove rows where the passenger count is equal to 0 and the trip distance is equal to zero. We can filter this by using:
    ```python
    data = data[(data['passenger_count'] > 0) & (data['trip_distance'] > 0)]
    ```
- Create a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date. We can use the `pd.to_datetime()` method to convert the column to datetime and then extract the date part.
    ```python
    data['lpep_pickup_date'] = pd.to_datetime(data['lpep_pickup_datetime']).dt.date
    ```
- Rename columns in Camel Case to Snake Case. We can use the `rename()` method to rename the columns. For converting the case, we can create `to_snake_case()` function to convert the column names to snake case.
    ```python
    def to_snake_case(column_name):
        name = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', column_name)
        return '_'.join(map(str.lower, name))

    data.rename(columns=lambda x: to_snake_case(x), inplace=True)
    ```
- Add three assertions in `@test` block to check the following:
    - `vendor_id` is one of the existing values in the column (currently)
    - `passenger_count` is greater than 0
    - `trip_distance` is greater than 0

Here is the full code for the transformer block:

```python
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd
import re

def to_snake_case(column_name):
    name = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', column_name)
    return '_'.join(map(str.lower, name))


@transformer
def transform(data, *args, **kwargs):
    # Remove rows that have passenger count = 0 and trip distance = 0
    data = data[(data['passenger_count'] > 0) & (data['trip_distance'] > 0)]
    
    # Convert to datetime
    data['lpep_pickup_date'] = pd.to_datetime(data['lpep_pickup_datetime']).dt.date

    # Rename columns from camel case to snake case
    data.rename(columns=lambda x: to_snake_case(x), inplace=True)

    return data

@test
def test_output(output, *args) -> None:
    assert 'vendor_id' in output.columns, 'There is no vendor_id in the existing columns'
    assert output['passenger_count'].isin([0]).sum() == 0, 'There are rides with zero passenger'
    assert output['trip_distance'].isin([0]).sum() == 0, 'There are rides with zero trip distance'
```

### Data Exporting
We will export the transformed data to Postgres and GCS. We are going to use the Data Exporter block that we have created previously.

Export data to Postgres:
- In the file explorer at the sidebar, in the `data_explorer` folder, drag the `data_to_postgres.py` file to the pipeline canvas. Change the `schema_name` and `table_name` to `mage` and `green_taxi` respectively. 
- Connect the block to the transformer block (downstream) and run the pipeline.
- To verify the exported data, we can use Data Loader block (SQL), choose PostgreSQL for the connection and `dev` for the profile (or the name of the config profile in the data exporter). Run the following query:
    ```sql
    SELECT *
    from mage.green_taxi
    ```
Code:
```python
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:
    schema_name = 'mage'  # Specify the name of the schema to export data to
    table_name = 'green_taxi'  # Specify the name of the table to export data to
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'dev'

    with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.export(
            df,
            schema_name,
            table_name,
            index=False,  # Specifies whether to include index in exported table
            if_exists='replace',  # Specify resolution policy if table name already exists
        )
```


Export data to GCS by partition in parquet format:
- In the file explorer at the sidebar, in the `data_explorer` folder, drag the `taxi_to_gcs_partitioned_parquet.py` file to the pipeline canvas. Change the `bucket_name` and `table_name` to the appropriate values.
- Change the `partition_cols` in `pq.write_to_dataset()` to `['lpep_pickup_date']`
- Connect the block to the transformer block (downstream) and run the pipeline.
- To verify the exported data, we can use the GCP Console to check the exported data in the bucket. Go to the Cloud Storage and verify the exported data.

Code: 
```python
import pyarrow as pa 
import pyarrow.parquet as pq 
import os

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_service_account.json"

bucket_name = "bucket_name"
project_id = "your_project_id"
table_name = "table_name"

root_path = f'{bucket_name}/{table_name}'

@data_exporter
def export_data(data, *args, **kwargs):
    table = pa.Table.from_pandas(data)
    gcs = pa.fs.GcsFileSystem()

    pq.write_to_dataset(
        table,
        root_path = root_path,
        partition_cols = ["lpep_pickup_date"],
        filesystem = gcs
    )
```

## Questions
### Q1
Q: Once the dataset is loaded, what's the shape of the data?   
A: 366,855 rows x 20 columns

### Q2
Q: Upon filtering the dataset where the passenger count is greater than 0 and the trip distance is greater than 0, how many rows are left?   
A: 139,370 rows

### Q3
Q: Which of the following creates a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date?    
A: `data["lpep_pickup_date"] = data["lpep_pickup_datetime"].dt.date`

### Q4
Q: What are the existing values of `VendorID` in the dataset?    
A: 

### Q5
Q: How many columns need to be renamned to snake case?    
A: 4

### Q6
Q: Once exported, how many partitions (folders) are present in Google Cloud?   
A: 96   