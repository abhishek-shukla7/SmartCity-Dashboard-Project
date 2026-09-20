
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Smart City Infrastructure Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
AQI_PATH = BASE_DIR / "Datasets" / "cleaned" / "Air_Quality.csv"
ENERGY_PATH = BASE_DIR / "Datasets" / "raw" / "Energy_usage_zone.csv"
TRAFFIC_PATH = BASE_DIR / "Datasets" / "raw" / "Traffic_usage_zone.csv"

NAVY = "#0B2239"
PANEL = "#102F4D"
BLUE = "#1EA7FF"
GREEN = "#00C853"
YELLOW = "#FFB300"
RED = "#FF1F1F"
WHITE = "#F5F9FF"
MUTED = "#AFC5D9"

CITY_COORDS = {
    "Amaravati": (16.5062, 80.6480), "Amritsar": (31.6340, 74.8723),
    "Brajrajnagar": (21.8160, 83.9160), "Chandigarh": (30.7333, 76.7794),
    "Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558),
    "Delhi": (28.6139, 77.2090), "Ernakulam": (9.9816, 76.2999),
    "Gurugram": (28.4595, 77.0266), "Hyderabad": (17.3850, 78.4867),
    "Jaipur": (26.9124, 75.7873), "Jorapokhar": (23.7400, 86.4130),
    "Kochi": (9.9312, 76.2673), "Kolkata": (22.5726, 88.3639),
    "Lucknow": (26.8467, 80.9462), "Mumbai": (19.0760, 72.8777),
    "Patna": (25.5941, 85.1376), "Shillong": (25.5788, 91.8933),
    "Talcher": (20.9500, 85.2200), "Thiruvananthapuram": (8.5241, 76.9366),
    "Visakhapatnam": (17.6868, 83.2185),
}

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #061522 0%, {NAVY} 55%, #061522 100%);
        color: {WHITE};
    }}
    [data-testid="stSidebar"] {{ background: #081C2E; border-right: 1px solid #1EA7FF55; }}
    [data-testid="stSidebar"] * {{ color: {WHITE}; }}
    .block-container {{ padding-top: 1.2rem; max-width: 1500px; }}
    .hero {{
        background: linear-gradient(90deg, #0D3151, #123B61);
        border: 1px solid {BLUE}; border-radius: 16px; padding: 20px 26px;
        box-shadow: 0 0 22px #008CFF55; margin-bottom: 18px;
    }}
    .hero-title {{ font-size: 30px; font-weight: 800; margin: 0; }}
    .hero-sub {{ color: {MUTED}; margin-top: 4px; }}
    .card {{
        background: rgba(16,47,77,.92); border: 1px solid #168EFF88;
        border-radius: 14px; padding: 14px 16px; min-height: 110px;
        box-shadow: 0 0 14px #008CFF2A;
    }}
    .card-label {{ color: {MUTED}; font-size: 13px; }}
    .card-value {{ color: {WHITE}; font-size: 29px; font-weight: 800; margin-top: 5px; }}
    .card-help {{ color: #88A8BF; font-size: 11px; margin-top: 4px; }}
    .section-title {{ font-size: 19px; font-weight: 750; margin: 4px 0 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner="Loading dashboard data…")
def load_data():
    aqi = pd.read_csv(AQI_PATH)
    aqi["Date"] = pd.to_datetime(aqi["Date"], errors="coerce")
    aqi["AQI"] = pd.to_numeric(aqi["AQI"], errors="coerce")
    aqi = aqi.dropna(subset=["Date"])

    ew = pd.read_csv(ENERGY_PATH)
    ew["Date"] = pd.to_datetime(ew["Unnamed: 0"], errors="coerce", dayfirst=True)
    energy_cols = [c for c in ew.columns if c not in ["Unnamed: 0", "Date"]]
    energy = ew.melt(
        id_vars=["Date"], value_vars=energy_cols,
        var_name="Zone_Name", value_name="Energy_Usage"
    )
    energy["Energy_Usage"] = pd.to_numeric(energy["Energy_Usage"], errors="coerce")
    energy = energy.dropna(subset=["Date", "Energy_Usage"])

    traffic = pd.read_csv(TRAFFIC_PATH)
    traffic["Date"] = pd.to_datetime(traffic["Date"], errors="coerce")
    for col in ["Fine_Amount", "Penalty_Points", "Recorded_Speed", "Speed_Limit", "Vehicle_Model_Year"]:
        if col in traffic.columns:
            traffic[col] = pd.to_numeric(traffic[col], errors="coerce")
    traffic = traffic.dropna(subset=["Date"])
    return aqi, energy, traffic

AQI, ENERGY, TRAFFIC = load_data()

def aqi_status(value):
    if pd.isna(value): return "Unknown"
    if value <= 100: return "Good"
    if value <= 150: return "Moderate"
    return "Unhealthy"

def fmt(value, digits=2):
    return "—" if pd.isna(value) else f"{value:,.{digits}f}"

def card(label, value, help_text=""):
    st.markdown(
        f"""<div class="card"><div class="card-label">{label}</div>
        <div class="card-value">{value}</div><div class="card-help">{help_text}</div></div>""",
        unsafe_allow_html=True,
    )

def hero(title, subtitle="Interactive Streamlit version of the Smart City Power BI project"):
    st.markdown(
        f"""<div class="hero"><div class="hero-title">{title}</div>
        <div class="hero-sub">{subtitle}
        <span style="float:right;font-weight:700;color:{WHITE}">ABHISHEK SHUKLA</span>
        </div></div>""",
        unsafe_allow_html=True,
    )

def style_fig(fig, height=390):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7,30,50,.35)", font=dict(color=WHITE),
        margin=dict(l=20, r=20, t=50, b=35), height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor="#31516B", zerolinecolor="#31516B")
    fig.update_yaxes(gridcolor="#31516B", zerolinecolor="#31516B")
    return fig

def date_slider(label, df, key):
    dmin, dmax = df["Date"].min().date(), df["Date"].max().date()
    return st.slider(label, dmin, dmax, (dmin, dmax), key=key)

def city_map(frame, value_col="AQI", title="City-wide sensor map"):
    # Use a manual Scattergeo trace instead of Plotly Express' size/color mapping.
    # This avoids a Plotly validator issue on Streamlit Cloud while preserving the
    # interactive AQI map and hover values.
    coords = pd.DataFrame(
        [(k, v[0], v[1]) for k, v in CITY_COORDS.items()],
        columns=["Zone_Name", "lat", "lon"]
    )
    m = frame.merge(coords, on="Zone_Name", how="left").dropna(subset=["lat", "lon"]).copy()
    if m.empty:
        st.info("No mapped city data is available for the selected filters.")
        return

    m[value_col] = pd.to_numeric(m[value_col], errors="coerce")
    m = m.dropna(subset=[value_col])
    if m.empty:
        st.info("No numeric metric values are available for the selected filters.")
        return

    vals = m[value_col].astype(float).to_numpy()
    fig = go.Figure(
        go.Scattergeo(
            lat=m["lat"].astype(float).to_numpy(),
            lon=m["lon"].astype(float).to_numpy(),
            text=m["Zone_Name"].astype(str),
            customdata=vals,
            mode="markers",
            marker=dict(
                size=13,
                color=vals,
                colorscale=[[0.0, "#00C853"], [0.5, "#FFB300"], [1.0, "#FF1F1F"]],
                cmin=float(vals.min()),
                cmax=float(vals.max()) if float(vals.max()) > float(vals.min()) else float(vals.min()) + 1,
                colorbar=dict(title=value_col),
                line=dict(width=1, color="#FFFFFF")
            ),
            hovertemplate="<b>%{text}</b><br>" + value_col + ": %{customdata:.2f}<extra></extra>"
        )
    )
    fig.update_geos(
        scope="asia", projection_type="natural earth",
        showland=True, landcolor="#17324A",
        showocean=True, oceancolor="#061522",
        showcountries=True, countrycolor="#58748B",
        coastlinecolor="#58748B"
    )
    fig.update_layout(title=title)
    st.plotly_chart(style_fig(fig, 460), use_container_width=True)

def metric_series(metric, start, end):
    if metric == "AQI":
        d = AQI[(AQI.Date.dt.date >= start) & (AQI.Date.dt.date <= end)]
        s = d.groupby("Date", as_index=False)["AQI"].mean().rename(columns={"AQI":"Value"})
        return s, "Average AQI"
    if metric == "Energy":
        d = ENERGY[(ENERGY.Date.dt.date >= start) & (ENERGY.Date.dt.date <= end)]
        s = d.groupby("Date", as_index=False)["Energy_Usage"].sum().rename(columns={"Energy_Usage":"Value"})
        return s, "Total Energy Usage"
    d = TRAFFIC[(TRAFFIC.Date.dt.date >= start) & (TRAFFIC.Date.dt.date <= end)]
    s = d.groupby("Date", as_index=False)["Fine_Amount"].sum().rename(columns={"Fine_Amount":"Value"})
    return s, "Total Traffic Fines"

st.sidebar.markdown("## 🏙️ Smart City")
st.sidebar.caption("Infrastructure & analytics portfolio dashboard")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Map & Sensor View", "Trends & Forecasts", "Alerts & Thresholds", "Zone Detail"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Data sources")
st.sidebar.caption("Air Quality • Energy Usage • Traffic Violations")

if page == "Overview":
    hero("SMART CITY INFRASTRUCTURE DASHBOARD")
    c1, c2, c3, c4 = st.columns(4)
    avg_aqi = AQI["AQI"].mean()
    above = (AQI["AQI"] > 150).mean()
    total_energy = ENERGY["Energy_Usage"].sum()
    total_fines = TRAFFIC["Fine_Amount"].sum()
    with c1: card("Average AQI", fmt(avg_aqi), "Mean of available AQI observations")
    with c2: card("Zones Above AQI 150", f"{above:.0%}", "Share of AQI records above threshold")
    with c3: card("Energy Usage", f"{total_energy/1e6:,.2f}M", "Sum of supplied energy observations")
    with c4: card("Total Traffic Fines", f"₹{total_fines/1e6:,.2f}M", "Sum of Fine_Amount")

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section-title">Energy Consumption Over Time</div>', unsafe_allow_html=True)
        e = ENERGY.groupby("Date", as_index=False)["Energy_Usage"].sum()
        fig = px.line(e, x="Date", y="Energy_Usage")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
    with right:
        st.markdown('<div class="section-title">AQI Over Time</div>', unsafe_allow_html=True)
        a = AQI.groupby("Date", as_index=False)["AQI"].mean()
        fig = px.line(a, x="Date", y="AQI")
        fig.add_hline(y=150, line_dash="dash", line_color=RED, annotation_text="AQI 150")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)

    a, b, c = st.columns([1, 1, 1.5])
    with a:
        health = max(0, 100 - AQI["AQI"].mean()/3)
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=health,
            gauge={"axis":{"range":[0,100]}, "bar":{"color":GREEN}}
        ))
        fig.update_layout(title="City Health Index")
        st.plotly_chart(style_fig(fig, 280), use_container_width=True)
    with b:
        top = AQI.groupby("Zone_Name", as_index=False)["AQI"].mean().nlargest(8, "AQI").sort_values("AQI")
        fig = px.bar(top, x="AQI", y="Zone_Name", orientation="h", color="AQI",
                     color_continuous_scale=["#00C853","#FFB300","#FF1F1F"])
        fig.update_layout(title="Top AQI Zones")
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)
    with c:
        city_map(AQI.groupby("Zone_Name", as_index=False)["AQI"].mean(), "AQI", "Average AQI by city")

    st.caption(
        "The supplied cleaned AQI file contains observations through July 2020; "
        "the project documentation describes a broader 2015–2025 scope. This deployment uses the supplied data files."
    )

elif page == "Map & Sensor View":
    hero("CITY WIDE SENSOR MAP")
    metric = st.radio("Select Metric", ["AQI", "Energy", "Traffic"], horizontal=True)
    if metric == "AQI":
        start, end = date_slider("Date Filter", AQI, "map_aqi_date")
        d = AQI[(AQI.Date.dt.date >= start) & (AQI.Date.dt.date <= end)]
        zone_metric, value_col = d.groupby("Zone_Name", as_index=False)["AQI"].mean(), "AQI"
        city_map(zone_metric, "AQI", "AQI sensor map")
    elif metric == "Energy":
        start, end = date_slider("Date Filter", ENERGY, "map_energy_date")
        d = ENERGY[(ENERGY.Date.dt.date >= start) & (ENERGY.Date.dt.date <= end)]
        zone_metric, value_col = d.groupby("Zone_Name", as_index=False)["Energy_Usage"].sum(), "Energy_Usage"
        st.info("Energy is stored at state/zone level in the supplied dataset.")
    else:
        start, end = date_slider("Date Filter", TRAFFIC, "map_traffic_date")
        d = TRAFFIC[(TRAFFIC.Date.dt.date >= start) & (TRAFFIC.Date.dt.date <= end)]
        zone_metric = d.groupby("Location", as_index=False)["Fine_Amount"].sum().rename(columns={"Location":"Zone_Name"})
        value_col = "Fine_Amount"
        st.info("Traffic is stored at region/state level in the supplied dataset.")

    x, y = st.columns(2)
    with x:
        top = zone_metric.nlargest(5, value_col).sort_values(value_col)
        fig = px.bar(top, x=value_col, y="Zone_Name", orientation="h", color=value_col,
                     color_continuous_scale=["#00C853","#FFB300","#FF1F1F"], title="Top 5 Zones")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with y:
        if metric == "AQI":
            t = d.groupby("Date", as_index=False)["AQI"].mean()
            ycol = "AQI"
        elif metric == "Energy":
            t = d.groupby("Date", as_index=False)["Energy_Usage"].sum()
            ycol = "Energy_Usage"
        else:
            t = d.groupby("Date", as_index=False)["Fine_Amount"].sum()
            ycol = "Fine_Amount"
        fig = px.line(t, x="Date", y=ycol, title="Metric Trend Over Time")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    sensor_table = AQI.groupby("Zone_Name").agg(
        Avg_AQI=("AQI","mean"), Min_AQI=("AQI","min"),
        Max_AQI=("AQI","max"), Records=("AQI","count")
    ).reset_index().sort_values("Avg_AQI", ascending=False)
    st.markdown('<div class="section-title">AQI Sensor Summary</div>', unsafe_allow_html=True)
    st.dataframe(sensor_table.style.format({
        "Avg_AQI":"{:.2f}", "Min_AQI":"{:.0f}", "Max_AQI":"{:.0f}"
    }), use_container_width=True, hide_index=True)

elif page == "Trends & Forecasts":
    hero("TRENDS & FORECASTS")
    metric = st.selectbox("Metric", ["AQI","Energy","Traffic"])
    source = {"AQI":AQI, "Energy":ENERGY, "Traffic":TRAFFIC}[metric]
    start, end = date_slider("Date Filter", source, f"trend_{metric}")
    series, label = metric_series(metric, start, end)
    if series.empty:
        st.warning("No data for the selected range.")
        st.stop()
    monthly = series.set_index("Date").resample("MS")["Value"].mean().reset_index()

    left, right = st.columns([1.2, 1])
    with left:
        fig = px.line(monthly, x="Date", y="Value", markers=True, title=f"{label} — monthly trend")
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)
    with right:
        latest, first = monthly.iloc[-1]["Value"], monthly.iloc[0]["Value"]
        change = ((latest-first)/first*100) if first else np.nan
        m1, m2 = st.columns(2)
        with m1: st.metric("Latest", f"{latest:,.2f}")
        with m2: st.metric("Change vs first", f"{change:+.1f}%")
        if len(monthly) >= 3:
            x = np.arange(len(monthly)); y = monthly["Value"].to_numpy(float)
            slope, intercept = np.polyfit(x, y, 1)
            future_x = np.arange(len(monthly), len(monthly)+3)
            future_y = intercept + slope*future_x
            future_dates = pd.date_range(
                monthly["Date"].max()+pd.offsets.MonthBegin(1), periods=3, freq="MS"
            )
            f = pd.DataFrame({"Date":future_dates, "Value":future_y})
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly["Date"], y=monthly["Value"], mode="lines", name="Actual"))
            fig.add_trace(go.Scatter(x=f["Date"], y=f["Value"], mode="lines+markers", name="Linear forecast"))
            fig.update_layout(title="Next 3 monthly periods")
            st.plotly_chart(style_fig(fig, 330), use_container_width=True)
        else:
            st.info("At least three monthly observations are needed for the forecast.")

    x, y = st.columns(2)
    with x:
        v = TRAFFIC.groupby("Vehicle_Color", as_index=False).size().rename(columns={"size":"Vehicle_Count"})
        fig = px.area(v, x="Vehicle_Color", y="Vehicle_Count", title="Vehicle Flow Rate by Color")
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)
    with y:
        ft = TRAFFIC.groupby("Date", as_index=False).agg(
            TotalFines=("Fine_Amount","sum"),
            AvgRecordedSpeed=("Recorded_Speed","mean")
        )
        fig = px.line(ft, x="Date", y=["TotalFines","AvgRecordedSpeed"], title="Fines and Recorded Speed")
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)

elif page == "Alerts & Thresholds":
    hero("ALERT & THRESHOLDS")
    left, center, right = st.columns([1.15, 1.25, .8])
    with left:
        start, end = date_slider("Select Date Range", AQI, "alert_date")
        zones = st.multiselect("Select Zone", sorted(AQI.Zone_Name.dropna().unique()), default=[])
        d = AQI[(AQI.Date.dt.date >= start) & (AQI.Date.dt.date <= end)].copy()
        if zones: d = d[d.Zone_Name.isin(zones)]
        zone_avg = d.groupby("Zone_Name", as_index=False)["AQI"].mean().rename(columns={"AQI":"AvgAQI"})
        zone_avg["AQI_Status"] = zone_avg.AvgAQI.apply(aqi_status)
        zone_avg = zone_avg.sort_values("AvgAQI")
        fig = px.bar(
            zone_avg, x="AvgAQI", y="Zone_Name", orientation="h",
            color="AQI_Status", color_discrete_map={"Good":GREEN,"Moderate":YELLOW,"Unhealthy":RED},
            text=zone_avg.AvgAQI.round(0), title="Average AQI by Zone (with Alert Levels)"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig, 520), use_container_width=True)
    with center:
        table = d[["Zone_Name","Date","AQI"]].copy()
        table["AvgAQI"] = table.groupby("Zone_Name")["AQI"].transform("mean")
        table["AQI_Status"] = table.AvgAQI.apply(aqi_status)
        table = table.rename(columns={"AQI":"Daily_AQI"})[
            ["Zone_Name","AvgAQI","AQI_Status","Date","Daily_AQI"]
        ].sort_values(["AvgAQI","Date"], ascending=[False,True])
        st.markdown('<div class="section-title">Zone-wise AQI Alert Table</div>', unsafe_allow_html=True)
        st.dataframe(table, use_container_width=True, hide_index=True, height=520)
    with right:
        counts = zone_avg.AQI_Status.value_counts().reindex(["Good","Moderate","Unhealthy"]).fillna(0)
        total = counts.sum()
        st.markdown('<div class="section-title">Zones according to AQI</div>', unsafe_allow_html=True)
        for status in ["Good","Moderate","Unhealthy"]:
            n = int(counts[status]); pct = n/total*100 if total else 0
            st.markdown(f"**{status}** — {n} zones ({pct:.1f}%)")
            st.progress(int(round(pct)))
        st.metric("Alert Threshold", "AQI > 150")
        st.metric("Average AQI", f"{zone_avg.AvgAQI.mean():.2f}" if not zone_avg.empty else "—")

else:
    hero("ZONE DETAIL VIEW")
    zone = st.selectbox("Select Zone", sorted(AQI.Zone_Name.dropna().unique()))
    z = AQI[AQI.Zone_Name == zone].copy()
    a, b, c = st.columns(3)
    with a: card("Average AQI", f"{z.AQI.mean():.2f}", zone)
    with b: card("Maximum AQI", f"{z.AQI.max():.0f}", "Highest recorded AQI")
    with c: card("Current Alert Level", aqi_status(z.AQI.mean()), "≤100 Good • ≤150 Moderate • >150 Unhealthy")

    x, y = st.columns([1, 1.5])
    with x:
        cat = z.AQI_Category.value_counts(dropna=False).reset_index()
        cat.columns = ["AQI_Category","Count"]
        cat["AQI_Category"] = cat.AQI_Category.fillna("Unknown")
        fig = px.pie(cat, names="AQI_Category", values="Count", hole=.35, title="AQI Status by Category")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
    with y:
        city_map(pd.DataFrame({"Zone_Name":[zone],"AQI":[z.AQI.mean()]}), "AQI", f"{zone} — sensor location")

    x, y = st.columns(2)
    with x:
        trend = z.groupby("Date", as_index=False)["AQI"].mean()
        fig = px.line(trend, x="Date", y="AQI", title=f"{zone} AQI over time")
        fig.add_hline(y=150, line_dash="dash", line_color=RED)
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with y:
        pollutants = ["PM2.5","PM10","NO2","NOx","NH3","CO","SO2","O3","Benzene","Toluene","Xylene"]
        profile = z[pollutants].mean().reset_index()
        profile.columns = ["Pollutant","Average"]
        fig = px.bar(profile.sort_values("Average"), x="Average", y="Pollutant", orientation="h", title="Pollutant Profile")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    energy_summary = ENERGY.groupby("Zone_Name", as_index=False)["Energy_Usage"].sum().nlargest(10, "Energy_Usage")
    fig = px.bar(
        energy_summary.sort_values("Energy_Usage"), x="Energy_Usage", y="Zone_Name",
        orientation="h", title="Energy Usage by State / Zone"
    )
    st.plotly_chart(style_fig(fig, 330), use_container_width=True)
    st.caption(
        "Energy remains at its native state/zone level because the supplied energy file does not contain "
        "a matching key for every AQI city."
    )
