# Gender Representation in Indian Cinema (2000–2024)
### A Bechdel Proxy Analysis of Hindi, Tamil & Telugu Films

---

## The Question

Does female representation in Indian films correlate with box office performance — and has it changed over 24 years?

The Bechdel Test (does a film have 2+ named women who talk about something other than a man?) has no structured database for Indian cinema. This project builds a proxy scoring system from cast and crew data, then quantifies its relationship with commercial success.

---

## Key Findings

- **Female cast representation has declined 40% since 2003** — from ~33% to ~18% of cast, despite increased public discourse around gender equality
- **Female-led films (Score 3) show higher median revenue** (₹150–200 cr) vs films with no female representation (Score 0, ~₹100 cr median) — though the Score 3 sample is small (11 films)
- **Only 6.7% of films (20/299) had female directors** — this has not meaningfully improved over the 24-year period
- **Budget remains the strongest revenue predictor** (β = 0.51 in log-linear regression), but female lead ratio adds a small positive signal (β = 0.09) even after controlling for budget, genre, and language
- **Hindi cinema skews more male-dominated** than Tamil or Telugu when normalised by sample size

---

## Methodology

### Data Collection
- **Source**: TMDB API (The Movie Database) — 299 films across Hindi, Tamil, and Telugu (2000–2024), filtered for vote count ≥ 100 to exclude obscure titles
- **Cast data**: Director gender, top-5 billed cast gender breakdown, full cast size
- **Box office**: Revenue and budget in USD from TMDB, converted to INR crore (₹1 cr = ₹10M) at 2024 average rate (₹83.5/$). 15 high-revenue films verified against Box Office India records

### Bechdel Proxy Score
Since bechdeltest.com's API was permanently shut down in 2025 and had minimal Indian film coverage, this project builds a structural proxy from cast composition:

| Score | Criteria |
|-------|----------|
| 0 | Fewer than 2 women in top 5 billed cast |
| 2 | 2+ women in top 5 cast, female ratio ≥ 40% |
| 3 | Score 2 criteria + female director |

**Important limitation**: This is a casting proxy, not a dialogue proxy. It measures structural representation, not narrative representation. Score 1 was absent in this dataset — films either had very few women or meaningful presence, with no middle ground.

### Modelling
- Linear Regression, Random Forest, and Gradient Boosting on log-transformed revenue
- Features: proxy score, female lead ratio, log budget, runtime, vote average, year, language dummies, genre dummies
- SHAP values used for feature importance and directional explanation
- Best model: Linear Regression (Test R² = 0.41, CV R² = 0.24)

---

## Limitations

1. **Sample size**: 299 films, with only 11 scoring 3 — findings are suggestive, not conclusive
2. **TMDB gender data gaps**: ~13% of cast have gender = 0 (unknown), likely underrepresenting women
3. **Revenue data**: TMDB box office is self-reported and incomplete — 101 films had no revenue data. Verified top 15 against external sources; others carry measurement error
4. **Proxy validity**: Casting composition ≠ screen time or dialogue. A film with 2 female leads who appear briefly could score 2
5. **Language imbalance**: 256 Hindi vs 43 South Indian films — findings are more robust for Hindi cinema

---

## Tools & Stack

| Tool | Purpose |
|------|---------|
| Python (requests, pandas, numpy) | Data collection and cleaning |
| Scikit-learn | Regression and model evaluation |
| SHAP | Model explainability |
| Plotly | Interactive dashboard |
| Power BI | Business intelligence dashboard |
| TMDB API | Primary data source |

---

## Repository Structure
indian-cinema-bechdel/
│
├── data/
│   ├── raw/                  # TMDB API pulls, unmodified
│   └── processed/            # Cleaned and feature-engineered datasets
│
├── notebooks/
│   ├── 01_data_collection.py
│   ├── 02_cleaning_eda.ipynb
│   ├── 03_regression.ipynb
│   └── 04_dashboard.ipynb
│
├── visuals/                  # All exported charts and dashboard HTML
├── README.md
└── requirements.txt

---

## How to Run

```bash
git clone https://github.com/yourusername/indian-cinema-bechdel
cd indian-cinema-bechdel
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Add your TMDB API key to .env
echo "TMDB_API_KEY=your_key_here" > .env

# Run in order
python notebooks/01_data_collection.py
# Then open notebooks 02, 03, 04 in Jupyter
```