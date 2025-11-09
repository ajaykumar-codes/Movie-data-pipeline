# Movie data pipeline

## Overview

* This project implements a complete **ETL (Extract, Transform, Load)** pipeline using **Python** and **MySQL**.
* The goal is to integrate data from the **MovieLens dataset** with movie metadata from the **OMDb API**.
* The ETL pipeline performs the following steps:

  * **Extract:** Read `movies.csv` and `ratings.csv` from the MovieLens dataset.
  * **Enrich:** Fetch additional details (Director, Plot, BoxOffice, Year) for the top movies using the OMDb API.
  * **Load:** Store the enriched movie data and corresponding ratings into a MySQL database.
* The final output allows analytical queries on movies, directors, and ratings using SQL.

---

## Environment Setup and Running the Project

### 1. Prerequisites

* Install **Python 3.8+**
* Install **MySQL 8.0+**
* Ensure `pip` is available in your system path


### 2. Create a Virtual Environment

```
python -m venv .venv
.venv\Scripts\activate

```

### 3. Install Required Libraries

```
pip install pandas requests sqlalchemy pymysql
```

### 4. Set Up the MySQL Database

1. Open MySQL command line or Workbench
2. Create a database:

   ```sql
   CREATE DATABASE moviedb;
   ```
3. Verify that MySQL is running.

### 5. Download the Dataset

* Download the **MovieLens Small Dataset** from:
  [https://grouplens.org/datasets/movielens/latest/](https://grouplens.org/datasets/movielens/latest/)
* Copy the following files into your project folder:

  * `movies.csv`
  * `ratings.csv`

### 6. Get an OMDb API Key

* Visit [http://www.omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx)
* Request a free API key.
* Open `etl.py` and replace:

  ```python
  OMDB_API_KEY = "your_api_key_here"
  ```

### 7. Run the ETL Script

```
python etl.py
```

### 8. Expected Output

```
Connecting to MySQL database...
Connection successful!
Extracting data from CSV files...
Calculating top-rated movies...
Fetching OMDb API data...
✅ Found: Won't You Be My Neighbor (2018)
✅ Found: Jane Eyre (1944)
❌ Not found: Rain (2001)
Filtering ratings for top movies only...
✅ ETL process completed successfully!
Inserted 10 movies and 3245 ratings into MySQL.
```

---

## 3. Design Choices and Assumptions

* Used **Python** for flexible data transformation and API integration.
* Used **pandas** for reading, merging, and cleaning CSV data.
* Used **SQLAlchemy** for connecting Python to MySQL seamlessly.
* Used **OMDb API** for real-world movie metadata enrichment.
* Implemented a **regex-based title cleaner** to remove “(Year)” from MovieLens titles and extract the year.
* Added a **rate limit delay (0.3 seconds)** to avoid hitting API limits.
* Used `if_exists="replace"` in `to_sql()` to make the ETL **idempotent** (safe to re-run multiple times).
* Filtered ratings to include **only top-N movies** for faster testing and reduced API calls.
* Assumed:

  * MovieLens CSVs follow the expected format (`movieId`, `title`, `genres`, etc.).
  * OMDb API key is valid and active.
  * Database user has permission to create or replace tables.

---

## 4. Challenges Faced and How They Were Solved

* **Issue:** OMDb returned “Movie not found” for some MovieLens titles.

  * **Solution:** Added a regex function `extract_title_and_year()` to clean titles and extract years before sending API requests.

* **Issue:** Hit OMDb’s free-tier API limit (1000 calls per day).

  * **Solution:** Introduced a variable `TOP_N = 10` to restrict enrichment to only top-rated movies during testing.

* **Issue:** Foreign key constraint errors in MySQL during table creation.

  * **Solution:** Removed foreign keys and used `if_exists="replace"` to allow clean recreation of tables each run.

* **Issue:** Data type mismatches (e.g., year and timestamp).

  * **Solution:** Used `pd.to_numeric(..., errors='coerce')` and timestamp conversion for consistent schema.

* **Issue:** Loading large number of ratings (100k+) slowed down inserts.

  * **Solution:** Filtered ratings to include only ratings for the top-N movies.

---

## Results

* Movies and ratings successfully loaded into **MySQL**.
* Enriched movie data includes:

  * Title
  * Genres
  * Average rating
  * Director (from OMDb)
  * Plot (from OMDb)
  * BoxOffice revenue
  * Year of release
* The ETL pipeline is repeatable, modular, and scalable.
* You can now run analytical queries in MySQL to find:

  * Highest-rated movies
  * Average rating by year
  * Director with the most highly-rated films

---

## Example SQL Queries for Analysis

* Find top 5 movies:

  ```sql
  SELECT title, rating, Director FROM movies ORDER BY rating DESC LIMIT 5;
  ```

* Find average rating per release year:

  ```sql
  SELECT year, AVG(rating) FROM movies WHERE year IS NOT NULL GROUP BY year ORDER BY year;
  ```

* Count total ratings per movie:

  ```sql
  SELECT movieId, COUNT(*) AS total_ratings FROM ratings GROUP BY movieId ORDER BY total_ratings DESC;
  ```

---

## Challenges for Future Improvement

* Implement API response caching to avoid re-fetching data for the same movie.
* Add proper logging (using Python’s logging library) instead of print statements.
* Dockerize the setup (Python + MySQL) for easier deployment.
* Integrate with Airflow or Prefect for scheduling and monitoring.
* Improve data normalization (separate genres into a lookup table).

---
