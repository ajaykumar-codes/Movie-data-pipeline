import pandas as pd
import requests
import time
import re
from sqlalchemy import create_engine

# CONFIGURATION

MOVIES_CSV = "movies.csv"
RATINGS_CSV = "ratings.csv"

# OMDb API key
OMDB_API_KEY = "2b6939b2"

# MySQL Database Config
DB_USER = "root"
DB_PASS = "12345678"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "moviedb"

# Limit API calls (set to None or 0 for full dataset)
TOP_N = 10

# DATABASE CONNECTION
print("Connecting to MySQL database...")
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print("Connection successful!")

# EXTRACT
print("\nExtracting data from CSV files...")

movies_df = pd.read_csv(MOVIES_CSV)
ratings_df = pd.read_csv(RATINGS_CSV)

print(f"Movies loaded: {len(movies_df)}")
print(f"Ratings loaded: {len(ratings_df)}")

# TRANSFORM — Get top N movies by average rating
print("\nCalculating top-rated movies...")
avg_ratings = (
    ratings_df.groupby("movieId")["rating"]
    .mean()
    .reset_index()
    .sort_values("rating", ascending=False)
)

movies_with_ratings = pd.merge(avg_ratings, movies_df, on="movieId", how="left")

if TOP_N:
    movies_with_ratings = movies_with_ratings.head(TOP_N)
    print(f"Limiting to top {TOP_N} movies for OMDb enrichment.")

# HELPER — Extract Clean Title and Year
def extract_title_and_year(title):
    match = re.search(r"\((\d{4})\)$", title)
    if match:
        year = match.group(1)
        clean_title = re.sub(r"\s+\(\d{4}\)$", "", title).strip()
        return clean_title, year
    return title, None


# ENRICH — Fetch details from OMDb API
def fetch_omdb_data(title):
    movie_title, movie_year = extract_title_and_year(title)
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    if movie_year:
        url += f"&y={movie_year}"

    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "True":
            print(f"✅ Found: {movie_title} ({movie_year})")
            return {
                "Director": data.get("Director"),
                "Plot": data.get("Plot"),
                "BoxOffice": data.get("BoxOffice"),
                "Year": data.get("Year"),
            }
        else:
            print(f"❌ Not found: {movie_title} ({movie_year})")
            return {"Director": None, "Plot": None, "BoxOffice": None, "Year": None}
    except Exception as e:
        print(f"Error fetching data for {movie_title}: {e}")
        return {"Director": None, "Plot": None, "BoxOffice": None, "Year": None}


print("\nFetching OMDb API data...")
omdb_info = []
for title in movies_with_ratings["title"]:
    print(f"Fetching: {title}")
    omdb_data = fetch_omdb_data(title)
    omdb_info.append(omdb_data)
    time.sleep(0.3)

omdb_df = pd.DataFrame(omdb_info)
movies_enriched = pd.concat([movies_with_ratings.reset_index(drop=True), omdb_df], axis=1)

# Clean data types
movies_enriched["year"] = pd.to_numeric(movies_enriched["Year"], errors="coerce")
movies_enriched.drop(columns=["Year"], inplace=True)
ratings_df["timestamp"] = pd.to_datetime(ratings_df["timestamp"], unit="s")

print("\nSample enriched movie data:")
print(movies_enriched[["title", "Director", "BoxOffice", "year"]].head())


# FILTER RATINGS for Top N Movies
print("\nFiltering ratings for top movies only...")
top_movie_ids = movies_enriched["movieId"].unique()
filtered_ratings = ratings_df[ratings_df["movieId"].isin(top_movie_ids)]

print(f"Filtered ratings: {len(filtered_ratings)} (only for {len(top_movie_ids)} movies)")


# LOAD — Save to MySQL
print("\nLoading data into MySQL...")

movies_enriched.to_sql("movies", engine, if_exists="replace", index=False)
filtered_ratings.to_sql("ratings", engine, if_exists="replace", index=False)

print("\n✅ ETL process completed successfully!")
print(f"Inserted {len(movies_enriched)} movies and {len(filtered_ratings)} ratings into MySQL.")
print("ETL process completed successfully!")
