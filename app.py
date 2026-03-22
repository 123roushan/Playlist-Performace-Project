import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Atlantic US Playlist Analytics", layout="wide")
st.title("🎵 Atlantic Records – US Playlist Analytics")
st.caption("Top 50 Streaming Chart | May 2024 – Nov 2025")

# --- Load & prep data ---
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\Admin\Desktop\Playlist Performance\Atlantic_United_States.csv")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["duration_min"] = df["duration_ms"] / 60000
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date range", [df["date"].min(), df["date"].max()])
artists = st.sidebar.multiselect("Artist", sorted(df["artist"].unique()))
rank_range = st.sidebar.slider("Chart position", 1, 50, (1, 50))
album_type = st.sidebar.multiselect("Album type", df["album_type"].unique(), default=list(df["album_type"].unique()))
explicit = st.sidebar.radio("Explicit", ["All", "Yes", "No"])

# apply filters
fdf = df.copy()
if len(date_range) == 2:
    fdf = fdf[(fdf["date"] >= pd.Timestamp(date_range[0])) & (fdf["date"] <= pd.Timestamp(date_range[1]))]
if artists:
    fdf = fdf[fdf["artist"].isin(artists)]
fdf = fdf[(fdf["position"] >= rank_range[0]) & (fdf["position"] <= rank_range[1])]
fdf = fdf[fdf["album_type"].isin(album_type)]
if explicit == "Yes":
    fdf = fdf[fdf["is_explicit"] == True]
elif explicit == "No":
    fdf = fdf[fdf["is_explicit"] == False]

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Unique Songs", fdf["song"].nunique())
k2.metric("Unique Artists", fdf["artist"].nunique())
k3.metric("Avg Popularity", f"{fdf['popularity'].mean():.1f}")
k4.metric("Explicit %", f"{fdf['is_explicit'].mean()*100:.1f}%")

st.divider()

# --- Song-level metrics ---
def song_stats(df):
    g = df.groupby(["song", "artist"])
    return g.agg(
        days_on_chart=("date", "nunique"),
        avg_rank=("position", "mean"),
        best_rank=("position", "min"),
        volatility=("position", "std"),
        avg_pop=("popularity", "mean"),
        album_type=("album_type", "first"),
        is_explicit=("is_explicit", "first"),
    ).round(2).reset_index()

songs = song_stats(fdf)

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Song Performance", "Artist Analysis", "Content Attributes"])

# Tab 1: Overview
with tab1:
    st.subheader("Monthly Chart Activity")
    monthly = fdf.groupby("month").agg(unique_songs=("song", "nunique"), avg_pop=("popularity", "mean")).reset_index()

    fig = go.Figure()
    fig.add_bar(x=monthly["month"], y=monthly["unique_songs"], name="Unique Songs", marker_color="#636EFA")
    fig.add_scatter(x=monthly["month"], y=monthly["avg_pop"].round(1), name="Avg Popularity",
                    yaxis="y2", line=dict(color="orange", width=2))
    fig.update_layout(
        yaxis=dict(title="Unique Songs"),
        yaxis2=dict(title="Avg Popularity", overlaying="y", side="right"),
        legend=dict(orientation="h"), height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most Days in Top 10")
    top10 = fdf[fdf["position"] <= 10].groupby("song")["date"].nunique().nlargest(12).reset_index()
    top10.columns = ["song", "days"]
    fig2 = px.bar(top10, x="days", y="song", orientation="h", color="days",
                  color_continuous_scale="Viridis", labels={"days": "Days in Top 10", "song": ""})
    fig2.update_layout(yaxis=dict(autorange="reversed"), height=380, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# Tab 2: Song Performance
with tab2:
    st.subheader("Top Songs by Days on Chart")
    n = st.slider("Show top N songs", 5, 30, 15)
    top_songs = songs.nlargest(n, "days_on_chart")

    fig3 = px.bar(top_songs, x="days_on_chart", y="song", orientation="h",
                  color="avg_pop", color_continuous_scale="RdYlGn",
                  hover_data=["artist", "avg_rank", "best_rank"],
                  labels={"days_on_chart": "Days on Chart", "song": "", "avg_pop": "Avg Pop"})
    fig3.update_layout(yaxis=dict(autorange="reversed"), height=480)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Rank Timeline")
    selected = st.multiselect("Pick songs to track", sorted(fdf["song"].unique()),
                              default=list(songs.nlargest(4, "days_on_chart")["song"]))
    if selected:
        tdf = fdf[fdf["song"].isin(selected)].groupby(["date", "song"])["position"].mean().reset_index()
        fig4 = px.line(tdf, x="date", y="position", color="song",
                       labels={"position": "Chart Position (lower = better)", "date": "Date"})
        fig4.update_yaxes(autorange="reversed")
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Song Metrics Table")
    st.dataframe(songs.sort_values("days_on_chart", ascending=False).reset_index(drop=True), use_container_width=True)

# Tab 3: Artist Analysis
with tab3:
    st.subheader("Artist Dominance")
    art = fdf.groupby("artist").agg(
        days=("date", "nunique"),
        songs=("song", "nunique"),
        avg_rank=("position", "mean"),
        avg_pop=("popularity", "mean")
    ).round(1).reset_index().sort_values("days", ascending=False)

    fig5 = px.bar(art.head(20), x="days", y="artist", orientation="h",
                  color="avg_pop", color_continuous_scale="Plasma",
                  hover_data=["songs", "avg_rank"],
                  labels={"days": "Total Chart Days", "artist": "", "avg_pop": "Avg Pop"})
    fig5.update_layout(yaxis=dict(autorange="reversed"), height=500)
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Catalog Size vs Popularity")
    fig6 = px.scatter(art.head(30), x="songs", y="avg_pop", size="days", color="avg_rank",
                      text="artist", color_continuous_scale="RdYlGn_r",
                      labels={"songs": "Unique Songs", "avg_pop": "Avg Popularity", "days": "Chart Days"})
    fig6.update_traces(textposition="top center", textfont_size=9)
    fig6.update_layout(height=420)
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Artist Monthly Appearances")
    pick = st.multiselect("Select artists", sorted(fdf["artist"].unique()),
                          default=list(art.head(5)["artist"]), key="art_monthly")
    if pick:
        adf = fdf[fdf["artist"].isin(pick)].groupby(["month", "artist"]).size().reset_index(name="entries")
        fig7 = px.line(adf, x="month", y="entries", color="artist",
                       labels={"entries": "Chart Entries", "month": "Month"})
        fig7.update_layout(height=320)
        st.plotly_chart(fig7, use_container_width=True)

# Tab 4: Content Attributes
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Explicit vs Clean")
        exp = fdf.groupby("is_explicit").agg(avg_rank=("position","mean"), avg_pop=("popularity","mean")).round(2).reset_index()
        exp["label"] = exp["is_explicit"].map({True: "Explicit", False: "Clean"})
        fig8 = px.bar(exp, x="label", y=["avg_rank", "avg_pop"], barmode="group",
                      labels={"value": "Score", "label": "", "variable": "Metric"})
        fig8.update_layout(height=300)
        st.plotly_chart(fig8, use_container_width=True)

    with c2:
        st.subheader("Album Type Performance")
        alb = fdf.groupby("album_type").agg(avg_pop=("popularity","mean"), count=("song","count")).round(1).reset_index()
        fig9 = px.bar(alb, x="album_type", y="avg_pop", color="album_type",
                      text="avg_pop", labels={"avg_pop": "Avg Popularity", "album_type": "Type"})
        fig9.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Song Duration vs Popularity")
    bins = [0, 2, 2.5, 3, 3.5, 4, 5, 10]
    labels = ["<2m", "2-2.5", "2.5-3", "3-3.5", "3.5-4", "4-5", ">5m"]
    fdf["dur_bucket"] = pd.cut(fdf["duration_min"], bins=bins, labels=labels)
    dur = fdf.groupby("dur_bucket", observed=True).agg(avg_pop=("popularity","mean"), avg_rank=("position","mean")).round(2).reset_index()
    fig10 = px.bar(dur, x="dur_bucket", y="avg_pop", color="avg_rank",
                   color_continuous_scale="RdYlGn_r", text="avg_pop",
                   labels={"dur_bucket": "Duration", "avg_pop": "Avg Popularity", "avg_rank": "Avg Rank"})
    fig10.update_layout(height=320)
    st.plotly_chart(fig10, use_container_width=True)

    st.subheader("Popularity vs Chart Position")
    sample = fdf.sample(min(800, len(fdf)), random_state=42)
    sample["explicit_label"] = sample["is_explicit"].map({True: "Explicit", False: "Clean"})
    fig11 = px.scatter(sample, x="position", y="popularity", color="explicit_label",
                       opacity=0.5, trendline="ols",
                       labels={"position": "Chart Position", "popularity": "Popularity Score"})
    fig11.update_layout(height=350)
    st.plotly_chart(fig11, use_container_width=True)