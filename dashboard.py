import streamlit as st
import pandas as pd
import duckdb
import os
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="GitHub Tech Trends Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme / Professional Styling
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stMetric { background-color: #1e222a; padding: 15px; border-radius: 10px; border: 1px solid #2d3139; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 GitHub Tech Trends — Gold Data Engineering Pipeline Dashboard")
st.caption("Real-time insights extracted, transformed, and loaded via Apache Airflow & DuckDB Gold layer.")

DUCKDB_PATH = os.path.join("data", "gold", "github_analytics.duckdb")

@st.cache_data(ttl=15)
def load_gold_data():
    if not os.path.exists(DUCKDB_PATH):
        return pd.DataFrame(), []
    
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    tables = [t[0] for t in conn.execute("SHOW TABLES;").fetchall()]
    
    if not tables:
        conn.close()
        return pd.DataFrame(), []
    
    table_name = tables[0]
    df = conn.execute(f"SELECT * FROM {table_name};").df()
    conn.close()
    return df, tables

df, tables = load_gold_data()

if df.empty:
    st.error("⚠️ Gold Layer empty or not found at `data/gold/github_analytics.duckdb`. Please run the Airflow pipeline.")
    st.stop()

# Auto-detect column names
star_col = next((c for c in ["stars", "stargazers_count", "star_count"] if c in df.columns), None)
lang_col = next((c for c in ["language", "primary_language"] if c in df.columns), None)
fork_col = next((c for c in ["forks", "forks_count", "fork_count"] if c in df.columns), None)
repo_col = next((c for c in ["name", "repo_name", "full_name"] if c in df.columns), None)
issue_col = next((c for c in ["open_issues", "open_issues_count"] if c in df.columns), None)

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters & Controls")
st.sidebar.success(f"Connected to DuckDB | Table: `{tables[0]}`")

if lang_col and df[lang_col].notnull().any():
    available_langs = sorted([str(x) for x in df[lang_col].dropna().unique()])
    selected_langs = st.sidebar.multiselect("Filter Languages:", available_langs, default=available_langs[:5])
    
    if selected_langs:
        filtered_df = df[df[lang_col].isin(selected_langs)]
    else:
        filtered_df = df
else:
    filtered_df = df

st.sidebar.markdown("---")
st.sidebar.info(f"Displaying **{len(filtered_df):,}** of **{len(df):,}** records.")

# --- TOP KPI METRICS ---
m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Total Repositories", f"{len(filtered_df):,}")

if star_col:
    m2.metric("Total Stars", f"{int(filtered_df[star_col].sum()):,}", delta=f"Avg {int(filtered_df[star_col].mean()):,}/repo")
else:
    m2.metric("Total Stars", "N/A")

if fork_col:
    m3.metric("Total Forks", f"{int(filtered_df[fork_col].sum()):,}")
else:
    m3.metric("Total Forks", "N/A")

if lang_col:
    m4.metric("Active Languages", filtered_df[lang_col].nunique())
else:
    m4.metric("Active Languages", "N/A")

if issue_col:
    m5.metric("Open Issues", f"{int(filtered_df[issue_col].sum()):,}")
else:
    m5.metric("Open Issues", "N/A")

st.markdown("---")

# --- ANALYTICS TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Language Market Share", "⭐ Top Repositories Analytics", "🔀 Engagement & Forks", "📁 Raw Gold Table Explorer"])

# TAB 1: LANGUAGES
with tab1:
    st.subheader("Programming Language Distribution")
    col1, col2 = st.columns(2)
    
    if lang_col:
        lang_counts = filtered_df[lang_col].value_counts().reset_index()
        lang_counts.columns = [lang_col, "count"]
        
        with col1:
            fig_bar = px.bar(
                lang_counts.head(10),
                x=lang_col,
                y="count",
                color="count",
                title="Top 10 Most Used Languages",
                labels={lang_col: "Language", "count": "Repository Count"},
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            fig_pie = px.pie(
                lang_counts.head(8),
                names=lang_col,
                values="count",
                title="Language Market Share (%)",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Language column not detected in dataset.")

# TAB 2: STARS & REPOSITORIES
with tab2:
    st.subheader("Most Starred Repositories")
    if repo_col and star_col:
        top_starred = filtered_df.nlargest(15, star_col)
        
        fig_stars = px.bar(
            top_starred,
            x=star_col,
            y=repo_col,
            orientation="h",
            color=star_col,
            title="Top 15 Most Starred Repositories",
            labels={star_col: "Stars", repo_col: "Repository"},
            color_continuous_scale="Viridis"
        )
        fig_stars.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_stars, use_container_width=True)
    else:
        st.warning("Star or Repository Name columns missing in Gold schema.")

# TAB 3: ENGAGEMENT (STARS VS FORKS)
with tab3:
    st.subheader("Community Engagement: Stars vs. Forks")
    if star_col and fork_col and repo_col:
        fig_scatter = px.scatter(
            filtered_df,
            x=star_col,
            y=fork_col,
            color=lang_col if lang_col else None,
            hover_name=repo_col,
            size=star_col,
            title="Scatter Plot: Stars vs. Forks per Repository",
            labels={star_col: "Stars", fork_col: "Forks"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("Forks, Stars, or Repository columns missing for scatter plotting.")

# TAB 4: RAW DATA EXPLORER & CSV EXPORT
with tab4:
    st.subheader("Explore & Export Gold Layer Data")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Gold Dataset as CSV",
        data=csv_data,
        file_name="gold_github_analytics.csv",
        mime="text/csv"
    )