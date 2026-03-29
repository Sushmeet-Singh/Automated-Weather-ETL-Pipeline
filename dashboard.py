import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Weather Pipeline Dashboard",
    page_icon="🌤",
    layout="wide"
)

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "weather_db",
    "user":     "postgres",
    "password": "root",
}

@st.cache_data(ttl=900)
def load_data():
    with psycopg2.connect(**DB_CONFIG) as conn:
        df = pd.read_sql("""
            SELECT city, country, temp_celsius, feels_like,
                   humidity, pressure_hpa, wind_speed,
                   description, fetched_at
            FROM weather_data
            ORDER BY fetched_at DESC
        """, conn)
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    return df

df = load_data()

if df.empty:
    st.warning("No data yet — run main.py first to collect some weather data.")
    st.stop()

latest = df.groupby("city").first().reset_index()

# ── sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("Controls")
    st.divider()

    # city selector
    all_cities = sorted(latest["city"].tolist())
    selected_cities = st.multiselect(
        "Select cities to display",
        options=all_cities,
        default=all_cities[:5]   # show 5 by default
    )

    st.divider()

    # metric to highlight
    metric = st.selectbox(
        "Highlight metric",
        options=["temp_celsius", "feels_like", "humidity", "wind_speed", "pressure_hpa"],
        format_func=lambda x: {
            "temp_celsius": "Temperature (°C)",
            "feels_like":   "Feels like (°C)",
            "humidity":     "Humidity (%)",
            "wind_speed":   "Wind speed (m/s)",
            "pressure_hpa": "Pressure (hPa)",
        }[x]
    )

    st.divider()

    # sort order
    sort_by = st.radio(
        "Sort cities by",
        options=["temp_celsius", "humidity", "wind_speed", "city"],
        format_func=lambda x: {
            "temp_celsius": "Temperature",
            "humidity":     "Humidity",
            "wind_speed":   "Wind speed",
            "city":         "City name",
        }[x]
    )
    sort_asc = st.checkbox("Ascending", value=False)

    st.divider()

    # cards per row slider
    cards_per_row = st.slider(
        "Cities per row",
        min_value=1,
        max_value=5,
        value=3
    )

    st.divider()

    # date range filter
    min_date = df["fetched_at"].min().date()
    max_date = df["fetched_at"].max().date()
    date_range = st.date_input(
        "Date range for charts",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    st.divider()
    st.caption("Pipeline runs every 15 minutes.")
    st.caption(f"Total records in DB: {len(df):,}")

# ── guard: nothing selected ───────────────────────────────────
if not selected_cities:
    st.warning("Select at least one city in the sidebar.")
    st.stop()

# ── filter & sort ─────────────────────────────────────────────
filtered_latest = latest[latest["city"].isin(selected_cities)].copy()
filtered_latest = filtered_latest.sort_values(sort_by, ascending=sort_asc)

# apply date range to trend data
if len(date_range) == 2:
    start, end = date_range
    trend_df = df[
        (df["city"].isin(selected_cities)) &
        (df["fetched_at"].dt.date >= start) &
        (df["fetched_at"].dt.date <= end)
    ]
else:
    trend_df = df[df["city"].isin(selected_cities)]

# ── header ────────────────────────────────────────────────────
st.title("Weather Analysis Dashboard")
st.caption(f"Last updated: {df['fetched_at'].max().strftime('%Y-%m-%d %H:%M')}  |  Showing {len(filtered_latest)} cities")

st.divider()

# ── current conditions cards (slider-controlled rows) ─────────
st.subheader("Current conditions")

cities_list = filtered_latest.to_dict("records")
for row_start in range(0, len(cities_list), cards_per_row):
    row_cities = cities_list[row_start:row_start + cards_per_row]
    cols = st.columns(cards_per_row)
    for col, row in zip(cols, row_cities):
        with col:
            delta_val = row["feels_like"] - row["temp_celsius"]
            delta_str = f"Feels like {row['feels_like']}°C  ({'+' if delta_val >= 0 else ''}{delta_val:.1f}°C)"

            st.metric(
                label=f"{row['city']}, {row['country']}",
                value=f"{row['temp_celsius']}°C",
                delta=delta_str
            )
            st.caption(f"{row['description'].title()}")
            st.caption(f"Humidity: {row['humidity']}%  |  Wind: {row['wind_speed']} m/s  |  Pressure: {row['pressure_hpa']} hPa")

st.divider()

# ── highlight metric bar chart ────────────────────────────────
metric_labels = {
    "temp_celsius": "Temperature (°C)",
    "feels_like":   "Feels like (°C)",
    "humidity":     "Humidity (%)",
    "wind_speed":   "Wind speed (m/s)",
    "pressure_hpa": "Pressure (hPa)",
}

st.subheader(f"City comparison — {metric_labels[metric]}")

fig_bar = px.bar(
    filtered_latest.sort_values(metric, ascending=True),
    x=metric,
    y="city",
    orientation="h",
    color=metric,
    color_continuous_scale="RdYlBu_r" if metric == "temp_celsius" else "Blues",
    text=metric,
    labels={metric: metric_labels[metric], "city": ""},
)
fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig_bar.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    height=400
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── temperature trends ────────────────────────────────────────
st.subheader("Temperature over time")

col1, col2 = st.columns([3, 1])
with col2:
    show_feels = st.checkbox("Show feels like", value=False)
    smooth     = st.checkbox("Smooth lines", value=False)

if trend_df.empty:
    st.info("No data for selected date range.")
else:
    if show_feels:
        trend_melt = trend_df.melt(
            id_vars=["city", "fetched_at"],
            value_vars=["temp_celsius", "feels_like"],
            var_name="type",
            value_name="temperature"
        )
        trend_melt["label"] = trend_melt["city"] + " — " + trend_melt["type"].map({
            "temp_celsius": "Actual",
            "feels_like":   "Feels like"
        })
        fig_trend = px.line(
            trend_melt,
            x="fetched_at",
            y="temperature",
            color="label",
            markers=not smooth,
            labels={"fetched_at": "Time", "temperature": "Temperature (°C)", "label": ""},
        )
    else:
        fig_trend = px.line(
            trend_df,
            x="fetched_at",
            y="temp_celsius",
            color="city",
            markers=not smooth,
            labels={"fetched_at": "Time", "temp_celsius": "Temperature (°C)", "city": "City"},
        )

    if smooth:
        fig_trend.update_traces(line_shape="spline")

    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        height=420
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── humidity & wind ───────────────────────────────────────────
st.subheader("Humidity vs wind speed")

col1, col2 = st.columns(2)

with col1:
    fig_hum = px.bar(
        filtered_latest.sort_values("humidity", ascending=False),
        x="city",
        y="humidity",
        color="humidity",
        color_continuous_scale="Blues",
        labels={"humidity": "Humidity (%)", "city": ""},
        text="humidity"
    )
    fig_hum.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_hum.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    st.plotly_chart(fig_hum, use_container_width=True)

with col2:
    fig_wind = px.bar(
        filtered_latest.sort_values("wind_speed", ascending=False),
        x="city",
        y="wind_speed",
        color="wind_speed",
        color_continuous_scale="Teal",
        labels={"wind_speed": "Wind speed (m/s)", "city": ""},
        text="wind_speed"
    )
    fig_wind.update_traces(texttemplate="%{text} m/s", textposition="outside")
    fig_wind.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    st.plotly_chart(fig_wind, use_container_width=True)

st.divider()

# ── scatter ───────────────────────────────────────────────────
st.subheader("Temperature vs humidity")
st.caption("Bubble size = wind speed. Hover over a city for full details.")

fig_scatter = px.scatter(
    filtered_latest,
    x="temp_celsius",
    y="humidity",
    color="city",
    size="wind_speed",
    text="city",
    hover_data={
        "temp_celsius": ":.1f",
        "feels_like":   ":.1f",
        "humidity":     True,
        "wind_speed":   ":.1f",
        "pressure_hpa": True,
        "description":  True,
        "city":         False,
    },
    labels={
        "temp_celsius": "Temperature (°C)",
        "humidity":     "Humidity (%)",
        "city":         "City"
    },
)
fig_scatter.update_traces(textposition="top center")
fig_scatter.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=450
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ── raw data ──────────────────────────────────────────────────
st.subheader("Raw data")

col1, col2 = st.columns([2, 1])
with col2:
    rows_to_show = st.select_slider(
        "Rows to show",
        options=[25, 50, 100, 250, 500],
        value=50
    )

st.dataframe(
    trend_df.head(rows_to_show),
    use_container_width=True,
    column_config={
        "temp_celsius": st.column_config.NumberColumn("Temp (°C)",       format="%.2f"),
        "feels_like":   st.column_config.NumberColumn("Feels like (°C)", format="%.2f"),
        "humidity":     st.column_config.NumberColumn("Humidity (%)"),
        "pressure_hpa": st.column_config.NumberColumn("Pressure (hPa)"),
        "wind_speed":   st.column_config.NumberColumn("Wind (m/s)",      format="%.2f"),
        "fetched_at":   st.column_config.DatetimeColumn("Fetched at",    format="DD/MM/YY HH:mm"),
    }
)