import pandas as pd
import numpy as np

df = pd.read_csv("./data/processed/indian_films_cleaned.csv")

export = df[[
    "title", "language_label", "year", "primary_genre",
    "director_gender_label", "female_leads_top5", "male_leads_top5",
    "female_cast_ratio", "female_lead_ratio", "total_cast",
    "female_in_full_cast", "bechdel_proxy_score", "bechdel_proxy_pass",
    "revenue_inr_crore", "budget_inr_crore", "roi",
    "vote_average", "runtime"
]].copy()

# Power BI doesn't like NaN in categorical columns
export["director_gender_label"] = export["director_gender_label"].fillna("Unknown")
export["primary_genre"] = export["primary_genre"].fillna("Unknown")

# Make proxy score a readable category
export["representation_tier"] = export["bechdel_proxy_score"].map({
    0.0: "No Representation",
    2.0: "Meaningful Presence",
    3.0: "Female-led & Directed"
}).fillna("Unknown")

# Round floats for cleaner display
export["female_cast_ratio"] = (export["female_cast_ratio"] * 100).round(1)  # as percentage
export["female_lead_ratio"] = (export["female_lead_ratio"] * 100).round(1)
export["roi"] = export["roi"].round(2)

export.to_csv("./data/powerbi_indian_cinema.csv", index=False)
print(f"✓ Exported {len(export)} rows")
print(export.dtypes)