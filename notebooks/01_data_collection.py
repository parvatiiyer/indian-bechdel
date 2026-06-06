import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# 1. PULL INDIAN FILMS FROM TMDB

def get_indian_movies(pages=25):
    """
    Pulls Hindi + Tamil + Telugu films from TMDB.
    25 pages × 20 results = ~500 films per language.
    """
    movies = []
    languages = ["hi", "ta", "te"]  # Hindi, Tamil, Telugu

    for lang in languages:
        print(f"\nFetching {lang} films...")
        for page in tqdm(range(1, pages + 1)):
            url = f"{BASE_URL}/discover/movie"
            params = {
                "with_original_language": lang,
                "sort_by": "popularity.desc",
                "page": page,
                "vote_count.gte": 100,       # filter out obscure films
                "primary_release_date.gte": "2000-01-01",
                "primary_release_date.lte": "2024-12-31",
            }
            r = requests.get(url, headers=HEADERS, params=params)
            if r.status_code != 200:
                print(f"Error on page {page}: {r.status_code}")
                break
            data = r.json().get("results", [])
            for m in data:
                m["language_queried"] = lang
            movies.extend(data)
            time.sleep(0.25)  

    df = pd.DataFrame(movies)
    df = df.drop_duplicates(subset="id")
    return df


# 2. ENRICH EACH FILM WITH CAST + CREW

def get_cast_crew(movie_id):
    """Returns cast list and director gender for a film."""
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None

    data = r.json()
    cast = data.get("cast", [])
    crew = data.get("crew", [])

    # Director info
    directors = [p for p in crew if p.get("job") == "Director"]
    director_gender = directors[0].get("gender", 0) if directors else 0
    # TMDB gender: 0 = unknown, 1 = female, 2 = male

    # Top 5 billed cast
    top_cast = cast[:5]
    female_leads = sum(1 for p in top_cast if p.get("gender") == 1)
    male_leads = sum(1 for p in top_cast if p.get("gender") == 2)

    return {
        "director_gender": director_gender,
        "female_leads_top5": female_leads,
        "male_leads_top5": male_leads,
        "total_cast": len(cast),
        "female_in_full_cast": sum(1 for p in cast if p.get("gender") == 1),
    }


def get_box_office(movie_id):
    """Returns budget, revenue, runtime from TMDB details endpoint."""
    url = f"{BASE_URL}/movie/{movie_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "budget": data.get("budget", 0),
        "revenue": data.get("revenue", 0),
        "runtime": data.get("runtime", 0),
        "genres": [g["name"] for g in data.get("genres", [])],
        "production_companies": [c["name"] for c in data.get("production_companies", [])],
    }


def enrich_movies(df):
    enriched = []
    print("\nEnriching films with cast + box office data...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        mid = row["id"]
        cast_data = get_cast_crew(mid)
        bo_data = get_box_office(mid)
        time.sleep(0.3)

        record = {
            "tmdb_id": mid,
            "title": row.get("title"),
            "original_language": row.get("original_language"),
            "language_queried": row.get("language_queried"),
            "release_date": row.get("release_date"),
            "popularity": row.get("popularity"),
            "vote_average": row.get("vote_average"),
            "vote_count": row.get("vote_count"),
        }
        if cast_data:
            record.update(cast_data)
        if bo_data:
            record.update(bo_data)

        enriched.append(record)

    return pd.DataFrame(enriched)

# BECHDEL PROXY SCORE

def build_bechdel_proxy(df):
    """
    Proxy Bechdel score using TMDB cast/crew data.

    0 = fewer than 2 women in top 5 cast
    1 = 2+ women in top 5 cast, but female ratio < 40%
    2 = 2+ women in top 5 cast, female ratio >= 40%, director male/unknown
    3 = 2+ women in top 5 cast, female ratio >= 40%, director female
    """

    def score_row(row):
        female_top5 = row.get("female_leads_top5", 0)
        total_top5 = (
            row.get("female_leads_top5", 0)
            + row.get("male_leads_top5", 0)
        )
        director_gender = row.get("director_gender", 2)

        if pd.isna(female_top5) or total_top5 == 0:
            return None

        female_ratio = female_top5 / total_top5

        if female_top5 < 2:
            return 0
        elif female_ratio < 0.4:
            return 1
        elif director_gender != 1:
            return 2
        else:
            return 3

    df["bechdel_proxy_score"] = df.apply(score_row, axis=1)
    df["bechdel_proxy_pass"] = df["bechdel_proxy_score"] == 3
    df["bechdel_proxy_partial"] = df["bechdel_proxy_score"] >= 2

    print("\nBechdel Proxy Score Distribution:")
    print(df["bechdel_proxy_score"].value_counts().sort_index())

    print(
        f"\nProxy Pass Rate: "
        f"{df['bechdel_proxy_pass'].mean():.1%}"
    )

    return df

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Step 1: Get base film list
    if not os.path.exists("data/raw/tmdb_indian_films_raw.csv"):
        print("=== STEP 1: Fetching Indian films from TMDB ===")
        raw_df = get_indian_movies(pages=25)
        raw_df.to_csv("data/raw/tmdb_indian_films_raw.csv", index=False)
        print(f"✓ Fetched {len(raw_df)} unique films")
    else:
        print("✓ STEP 1 already done, loading from file...")
        raw_df = pd.read_csv("data/raw/tmdb_indian_films_raw.csv")

    # Step 2: Enrich with cast + box office
    if not os.path.exists("data/raw/tmdb_enriched.csv"):
        print("\n=== STEP 2: Enriching with cast + box office ===")
        enriched_df = enrich_movies(raw_df)
        enriched_df.to_csv("data/raw/tmdb_enriched.csv", index=False)
        print(f"✓ Enriched {len(enriched_df)} films")
    else:
        print("✓ STEP 2 already done, loading from file...")
        enriched_df = pd.read_csv("data/raw/tmdb_enriched.csv")

        # Step 3: Build master dataset with proxy scores
    if not os.path.exists("data/processed/indian_films_master.csv"):
        print("\n=== STEP 3: Building master dataset ===")

        final_df = enriched_df.copy()

        final_df = build_bechdel_proxy(final_df)

        final_df.to_csv(
            "data/processed/indian_films_master.csv",
            index=False
        )

        print(f"\n✓ DONE. Master dataset: {len(final_df)} films")

        if "bechdel_proxy_score" in final_df.columns:
            print(
                f"  Films with proxy scores: "
                f"{final_df['bechdel_proxy_score'].notna().sum()}"
            )

        print(
            f"  Films with revenue > 0: "
            f"{(final_df['revenue'] > 0).sum()}"
        )

    else:
        print("✓ STEP 3 already done. Master dataset exists.")
        print("Next: open notebooks/02_cleaning_eda.ipynb")
