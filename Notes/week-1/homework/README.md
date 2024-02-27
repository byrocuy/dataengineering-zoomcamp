# Module 1 Homework

## 1. Docker & SQL
### Q1: Knowing Docker Tags

Instructions:
- Run the command `docker --help`
- Run the command `docker build --help`
- Run the command `docker run --help`

Questions:
Which tag has the following text? "Automatically remove the container when it exits"

Answer: 
`--rm`

### Q2: Understanding Docker First Run
Instructions:
- Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash. Now check the python modules that are installed (using `pip list`)

Questions:
- What is the version of the package `wheel`?

Answer:
`0.42.0`

## 2. Preparing Postgres

Instructions:
- Ingest the `green_tripdata_2019-09.csv.gz` [[link]](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz) to Postgres database using Jupyter Notebook or with a pipeline.

In this note, we will use Python pipeline to prepare the data using the same `pipeline.py` file used in this week's lesson. There are some changes needed in the code:
- When reading the csv using `pd.read_csv`, we need to specify the `compression` parameter to `gzip` because the file we are going to download is in gzip format.
- Change the parse dates from `tpep_pickup_datetime` and `tpep_dropoff_datetime` to `lpep_pickup_datetime` and `lpep_dropoff_datetime` because the column names are different in the `green_tripdata_2019-09.csv.gz` file.
- You can leave the rest of the code as is.

After the pipeline is created, run the following command to ingest the data to Postgres (don't forget to start the Postgres server first, you can use `docker-compose up` to start the Postgres server and pgAdmin):

```bash
python ingest_data.py ^
    --username root ^
    --password root ^
    --host localhost ^
    --port 5432 ^
    --db ny_taxi ^
    --table_name green_tripdata ^
    --url https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz
```
![Ingesting data green trip data to Postgres](../img/ingest-green-trip-data.png)

### Q3: Count Records

Question:
- How many trips were totally made on September 18th 2019?
Tip: started and finished on 2019-09-18. Remember that `lpep_pickup_datetime` and `lpep_dropoff_datetime` column are in the format timestamp (date and hour+min+sec) and not in date.

Answer:
We can query this using the following SQL query:
```sql
SELECT COUNT(*) AS count_dropoff
FROM green_tripdata
WHERE TO_DATE("lpep_dropoff_datetime", 'YYYY-MM-DD') = '2019-09-18'
AND TO_DATE("lpep_pickup_datetime", 'YYYY-MM-DD') = '2019-09-18'
```

Resulting: 15.612 records count

### Q4: Longest Trip for each Day

Question:
Which was the pick up day with the longest trip distance? Use the pickup time for you calulations
Tip: for every trip on a single day, we only care about the trip with the longest distance

Answer:
I lost on this one. sorry

### Q5: Three Biggest Pick Up Boroughs

Question:
Consider `lpep_pickup_datetime` in 2019-09-18 and ignoring Borough has unknown. Which are the 3 pick up Boroughs that had a sum of total_amount larger than 50.000?

Answer:
We can query this using the following SQL query:
```sql
SELECT z."Borough", ROUND(SUM(total_amount)::numeric,2) as total
FROM zones z
JOIN green_tripdata g
ON z."LocationID" = g."PULocationID"
WHERE TO_DATE(g.lpep_pickup_datetime, 'YYYY-MM-DD') = '2019-09-18'
GROUP BY z."Borough"
ORDER BY total DESC
LIMIT 3
```

Resulting: Brooklyn, Manhattan, and Queens

### Q6: Largest Tip

Question:
For the passengers pickeup up in September 2019 in the zone name `Astoria`, which was the dropoff zone that had the largest tip? We want the name of the zone, not the id.



## 3. Terraform
### Q7: Creating Resources