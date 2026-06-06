import pandas as pd
import numpy as np

df = pd.read_csv("./data/processed/indian_films_cleaned.csv")

# Fix 1: Lost Ladies revenue_clean
df.loc[df["title"] == "Lost Ladies", "revenue_clean"] = 3000000

# Fix 2: Theri — revenue of 69 rupees is clearly wrong
df.loc[df["title"] == "Theri", "revenue_clean"] = np.nan
df.loc[df["title"] == "Theri", "revenue_inr_crore"] = np.nan
df.loc[df["title"] == "Theri", "has_boxoffice"] = False

# Fix 3: Jailer has revenue_clean but no revenue_inr_crore — convert
jailer_mask = df["title"] == "Jailer"
df.loc[jailer_mask, "revenue_inr_crore"] = df.loc[jailer_mask, "revenue_clean"] * 83.5 / 1e7

df.to_csv("./data/processed/indian_films_cleaned.csv", index=False)
print("✓ Fixes applied")

# Verify top 15
bo = df[df["has_boxoffice"]].copy()
print("\nTOP 15 BY REVENUE (INR Crore):")
print(bo.nlargest(15, "revenue_inr_crore")[["title", "revenue_inr_crore", "bechdel_proxy_score", "language_label"]].to_string(index=False))