# 🎵 Playlist Analytics Dashboard

An interactive Streamlit dashboard for analyzing music playlist performance using Atlantic API data. Tracks chart positions, artist dominance, popularity trends, and content attributes across daily playlist snapshots.

---

## 📸 Overview

The dashboard covers 90 days of playlist data (Top 50 songs per day) and lets you explore:

- How songs rise, fall, and exit the charts
- Which artists dominate over time
- How popularity scores correlate with chart rank
- The impact of song duration, explicit content, and album type on performance

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+

### Installation

```bash
git clone https://github.com/your-username/playlist-analytics.git
cd playlist-analytics
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
playlist-analytics/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 📊 Dashboard Tabs

| Tab | What's Inside |
|-----|--------------|
| 📅 **Timeline** | Daily popularity trend, song rank trajectories over time |
| 🎵 **Songs** | Days on chart, peak rank vs longevity scatter, song leaderboard |
| 👤 **Artists** | Dominance index ranking, chart presence map, rank trends |
| 📊 **Popularity** | Popularity vs rank correlation, distribution by rank band, 7-day rolling average |
| 🔍 **Attributes** | Explicit vs clean split, single vs album comparison, duration impact, album size analysis |

---

## 🔧 Filters (Sidebar)

- **Date Range** — Narrow analysis to a specific time window
- **Rank Range** — Focus on Top 10, Top 20, or any custom range
- **Album Type** — Toggle between singles and albums
- **Artists** — Filter to one or more specific artists
- **Explicit Filter** — View all songs, explicit only, or clean only

All filters apply across every tab simultaneously.

---

## 📐 Key Metrics

| Metric | Description |
|--------|-------------|
| Days on Chart | How long a song stayed in the Top 50 |
| Average Rank | Mean chart position across all appearances |
| Best Rank | Highest (lowest number) position achieved |
| Rank Volatility | Standard deviation of daily rank |
| Avg Popularity | Mean Atlantic API popularity score |
| Dominance Index | Composite artist score (rank + songs + days) |

---

## 🗂️ Dataset Fields

| Field | Description |
|-------|-------------|
| `date` | Date of playlist snapshot |
| `position` | Playlist rank (1–50) |
| `song` | Song title |
| `artist` | Artist name(s) |
| `popularity` | Popularity score from Atlantic API |
| `duration_ms` | Song duration in milliseconds |
| `album_type` | Single or Album |
| `total_tracks` | Number of tracks in the album |
| `is_explicit` | Explicit content flag |

> **Note:** The app currently uses synthetically generated sample data. To use real data, replace the `load_data()` function in `app.py` with `pd.read_csv("your_data.csv")` and ensure your CSV matches the field names above.

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — Web app framework
- [Plotly Express](https://plotly.com/python/plotly-express/) — Interactive charts
- [Pandas](https://pandas.pydata.org/) — Data manipulation
- [NumPy](https://numpy.org/) — Numerical operations

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
