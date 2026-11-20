import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Color Palette --------------------
NAVY = "#0C2340"
DARK_NAVY = "#07172B"
YELLOW = "#FFD600"
BLUE = "#174EA6"
MID_BLUE = "#376DB0"
SOFT_BLUE = "#6699CC"
LIGHT_BLUE = "#91B9DF"
PALE_BLUE = "#B8D3EC"
DARK = "#0A1B33"

VEHICLE_COLORS = {
    "Prime Sedan": NAVY,
    "E-Bike": YELLOW,
    "Auto": BLUE,
    "Prime Plus": MID_BLUE,
    "Bike": SOFT_BLUE,
    "Prime SUV": LIGHT_BLUE,
    "Mini": PALE_BLUE,
}

PAYMENT_COLORS = {
    "Cash": YELLOW,
    "UPI": NAVY,
    "Credit Card": BLUE,
    "Debit Card": DARK
}

RANK_COLORS = [YELLOW, NAVY, BLUE, SOFT_BLUE, LIGHT_BLUE]

# -------------------- CSS Styling --------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Segoe UI', Inter, -apple-system, sans-serif;
}}

.stApp {{
    background: linear-gradient(135deg, #F0F4FA 0%, #FAFBFD 50%, #EEF4FB 100%);
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #07172B 0%, #0C2340 60%, #081B33 100%) !important;
    border-right: none;
    box-shadow: 4px 0 20px rgba(7, 23, 43, 0.15);
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.2rem;
    padding-bottom: 0;
}}

/* Custom Radio navigation buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] {{
    gap: 8px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
    gap: 9px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 9px 14px !important;
    color: #E2E8F0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
    cursor: pointer;
    margin: 2px 0;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: rgba(255, 255, 255, 0.12);
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
    background: {YELLOW} !important;
    border-color: {YELLOW} !important;
    color: {NAVY} !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 14px rgba(255, 214, 0, 0.35);
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * {{
    color: {NAVY} !important;
    font-weight: 800 !important;
}}

/* Page header */
.page-title {{
    font-size: 28px;
    font-weight: 800;
    color: {NAVY};
    letter-spacing: -0.3px;
    margin: 0;
    line-height: 1.2;
}}
.page-subtitle {{
    font-size: 13.5px;
    color: #556987;
    margin: 3px 0 16px;
    font-weight: 500;
}}

/* Robust Non-Overlapping KPI Cards */
.kpi-card {{
    background: #FFFFFF;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 10px rgba(12, 35, 64, 0.05);
    border: 1px solid #E8EEF5;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 94px;
    height: 100%;
    box-sizing: border-box;
    margin-bottom: 12px;
}}
.kpi-title {{
    font-size: clamp(11px, 0.9vw, 12.5px);
    font-weight: 600;
    color: #64748B;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.kpi-value {{
    font-size: clamp(20px, 1.8vw, 27px);
    font-weight: 800;
    color: {NAVY};
    letter-spacing: -0.4px;
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.kpi-title-bottom {{
    font-size: clamp(11px, 0.9vw, 12.5px);
    font-weight: 600;
    color: #64748B;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* Chart containers */
.chart-card {{
    background: #FFFFFF;
    border-radius: 10px;
    padding: 14px 16px 10px;
    box-shadow: 0 2px 10px rgba(12, 35, 64, 0.05);
    border: 1px solid #E8EEF5;
    margin-bottom: 14px;
    box-sizing: border-box;
}}
.chart-title {{
    font-size: 15.5px;
    font-weight: 700;
    color: {NAVY};
    text-align: center;
    margin-bottom: 6px;
}}

/* Filter Card */
.filter-card {{
    background: #FFFFFF;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 10px rgba(12, 35, 64, 0.05);
    border: 1px solid #E8EEF5;
}}
.filter-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: {NAVY};
    text-align: center;
    margin-bottom: 6px;
}}

div[data-testid="stPlotlyChart"] {{
    border-radius: 8px;
}}
</style>
""", unsafe_allow_html=True)

# -------------------- CSV Data Loading --------------------
@st.cache_data(show_spinner="Loading OLA ride data...")
def load_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaned_ola_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found: {csv_path}. Place cleaned_ola_data.csv in the same folder as app.py."
        )

    data = pd.read_csv(
    csv_path,
    header=None,
    names=[
        "Date", "Time", "Booking_ID", "Booking_Status",
        "Customer_ID", "Vehicle_Type", "Pickup_Location",
        "Drop_Location", "V_TAT", "C_TAT",
        "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
        "Incomplete_Rides", "Incomplete_Rides_Reason",
        "Booking_Value", "Payment_Method", "Ride_Distance",
        "Driver_Ratings", "Customer_Rating", "Vehicle Images"
    ],
    low_memory=False,
    na_values=["null", "NULL", "Null", "None", ""]
)

    required = [
        "Date", "Booking_ID", "Booking_Status", "Customer_ID", "Vehicle_Type",
        "Booking_Value", "Ride_Distance", "Payment_Method",
        "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
        "Incomplete_Rides", "Driver_Ratings", "Customer_Rating"
    ]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing columns in CSV file: " + ", ".join(missing))

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    for c in ["Booking_Value", "Ride_Distance", "Driver_Ratings", "Customer_Rating"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    for c in ["Booking_Status", "Vehicle_Type", "Payment_Method",
              "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver", "Incomplete_Rides"]:
        data[c] = data[c].astype("string").str.strip()
        data[c] = data[c].replace({"": pd.NA, "null": pd.NA, "NULL": pd.NA, "None": pd.NA})

    data["Date_Only"] = data["Date"].dt.date
    return data


try:
    df = load_data()
except Exception as e:
    st.error("Could not load OLA data from CSV. Check that cleaned_ola_data.csv is beside app.py and is a valid CSV.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("No records found in cleaned_ola_data.")
    st.stop()

# -------------------- Formatting Helpers --------------------
def fmt_plain(x):
    return f"{x:.0f}" if pd.notna(x) else "—"

def fmt_k(x, dec_m=2):
    if pd.isna(x): return "—"
    if abs(x) >= 1_000_000: return f"{x/1_000_000:.{dec_m}f}M"
    if abs(x) >= 1_000: return f"{x/1_000:.0f}K"
    return f"{x:,.0f}"

def fmt_money(x, dec_m=2):
    if pd.isna(x): return "₹ 0"
    if abs(x) >= 1_000_000: return f"₹ {x/1_000_000:.{dec_m}f}M"
    if abs(x) >= 1_000: return f"₹ {x/1_000:.1f}K"
    return f"₹ {x:,.1f}"

def chart_style(fig, height=310, show_legend=False):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=15, r=15, t=10, b=25),
        font=dict(family="Segoe UI, Inter, Arial", color="#475569", size=11.5),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        xaxis=dict(showgrid=True, gridcolor="#EDF2F7", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#EDF2F7", zeroline=False),
        showlegend=show_legend
    )
    return fig

def render_kpi(label, value, label_at_bottom=False):
    if label_at_bottom:
        html = f"""
        <div class="kpi-card">
            <div class="kpi-value" title="{value}">{value}</div>
            <div class="kpi-title-bottom" title="{label}">{label}</div>
        </div>
        """
    else:
        html = f"""
        <div class="kpi-card">
            <div class="kpi-title" title="{label}">{label}</div>
            <div class="kpi-value" title="{value}">{value}</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

# -------------------- Sidebar --------------------
with st.sidebar:
    # Top Logo: Uses image if present in assets, else high-fidelity markup
    if os.path.exists("assets/ola_logo.png"):
        st.image("assets/ola_logo.png", width=150)
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: left; padding: 4px 8px 16px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
                <div style="width: 28px; height: 28px; border-radius: 50%; background: {YELLOW}; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                    <div style="width: 14px; height: 14px; border-radius: 50%; background: #0A192F;"></div>
                </div>
                <span style="font-size: 28px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px; line-height: 1;">OLA</span>
            </div>
            <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-left: 2px;">Ride Insights</div>
            <div style="width: 50px; height: 3px; background: {YELLOW}; margin-top: 5px; border-radius: 2px;"></div>
        </div>
        """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overall", "Vehicle Analysis", "Revenue Analysis", "Cancellation Analysis", "Ratings Analysis"],
        label_visibility="collapsed"
    )

    # Bottom Illustration: Uses image file if present, else crisp inline SVG
    if os.path.exists("assets/ola_car_sidebar.png"):
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.image("assets/ola_car_sidebar.png", use_container_width=True)
    elif os.path.exists("assets/car.png"):
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.image("assets/car.png", use_container_width=True)
    else:
        st.markdown(f"""
        <div style="margin-top: 50px; position: relative; width: 100%; height: 175px; overflow: hidden; border-radius: 0 0 10px 10px;">
            <svg viewBox="0 0 300 200" style="width: 100%; height: 100%;" preserveAspectRatio="none">
                <!-- Skyline -->
                <rect x="25" y="65" width="22" height="95" fill="#0E2D52" opacity="0.8"/>
                <rect x="52" y="45" width="28" height="115" fill="#133863" opacity="0.9"/>
                <rect x="85" y="80" width="18" height="80" fill="#0E2D52" opacity="0.7"/>
                <rect x="108" y="55" width="25" height="105" fill="#154275" opacity="0.9"/>
                <rect x="138" y="70" width="30" height="90" fill="#0E2D52" opacity="0.8"/>
                <rect x="172" y="90" width="20" height="70" fill="#133863" opacity="0.7"/>
                <rect x="196" y="50" width="26" height="110" fill="#154275" opacity="0.85"/>
                <!-- Windows -->
                <circle cx="60" cy="60" r="1.5" fill="#88B8F0" opacity="0.7"/>
                <circle cx="60" cy="75" r="1.5" fill="#88B8F0" opacity="0.7"/>
                <circle cx="118" cy="70" r="1.5" fill="#88B8F0" opacity="0.7"/>
                <!-- Yellow Location Pin -->
                <g transform="translate(142, 68)">
                    <path d="M 0,0 C -6,0 -10,4.5 -10,10 C -10,17 0,26 0,26 C 0,26 10,17 10,10 C 10,4.5 6,0 0,0 Z" fill="{YELLOW}"/>
                    <circle cx="0" cy="9" r="4" fill="#07172B"/>
                </g>
                <!-- White Sedan Car -->
                <g transform="translate(30, 108)">
                    <path d="M 5,26 L 18,26 L 30,12 L 80,12 L 95,22 L 125,23 C 128,23 130,26 130,30 L 130,38 L 0,38 L 0,30 C 0,27 2,26 5,26 Z" fill="#FFFFFF"/>
                    <path d="M 33,14 L 54,14 L 54,23 L 25,23 Z" fill="#0E2D52"/>
                    <path d="M 58,14 L 78,14 L 90,23 L 58,23 Z" fill="#0E2D52"/>
                    <text x="50" y="33" font-family="Segoe UI, Arial" font-size="8" font-weight="900" fill="#0C2340">OLA</text>
                    <circle cx="28" cy="38" r="9" fill="#1E293B"/>
                    <circle cx="28" cy="38" r="5" fill="#94A3B8"/>
                    <circle cx="98" cy="38" r="9" fill="#1E293B"/>
                    <circle cx="98" cy="38" r="5" fill="#94A3B8"/>
                </g>
                <!-- Yellow Wave -->
                <path d="M 0,165 Q 90,140 180,165 T 300,160 L 300,200 L 0,200 Z" fill="{YELLOW}"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)

# -------------------- Filter State Management --------------------
if "filter_date" not in st.session_state:
    min_d = df["Date"].dropna().min().date()
    max_d = df["Date"].dropna().max().date()
    st.session_state["filter_date"] = (min_d, max_d)

if "filter_vehicle" not in st.session_state:
    st.session_state["filter_vehicle"] = "All"

# -------------------- Filter Application --------------------
data = df.copy()

if st.session_state["filter_date"] and len(st.session_state["filter_date"]) == 2:
    s_date, e_date = st.session_state["filter_date"]
    data = data[data["Date"].notna() & (data["Date"].dt.date >= s_date) & (data["Date"].dt.date <= e_date)]

if st.session_state["filter_vehicle"] != "All":
    data = data[data["Vehicle_Type"] == st.session_state["filter_vehicle"]]

if data.empty:
    st.warning("No records match the current filter selection.")
    st.stop()

# Key Calculated Metrics
success = data[data["Booking_Status"].eq("Success").fillna(False)]
customer_cancel = data[data["Booking_Status"].eq("Canceled by Customer").fillna(False)]
driver_cancel = data[data["Booking_Status"].eq("Canceled by Driver").fillna(False)]

bookings = data["Booking_ID"].nunique()
successful = success["Booking_ID"].nunique()
revenue = success["Booking_Value"].sum()
success_rate = (successful / bookings * 100) if bookings else 0.0

distance = data["Ride_Distance"].sum()
avg_distance = data["Ride_Distance"].mean()
avg_customer = data["Customer_Rating"].mean()
avg_driver = data["Driver_Ratings"].mean()

cust_cancel_n = customer_cancel["Booking_ID"].nunique()
driver_cancel_n = driver_cancel["Booking_ID"].nunique()
incomplete = (
    data["Incomplete_Rides"].astype("string").str.strip().str.lower()
    .isin(["yes", "y", "1", "1.0", "true"]).fillna(False).sum()
)

headers = {
    "Overall": ("OLA Ride Insights", "Overall performance and ride booking overview"),
    "Vehicle Analysis": ("Vehicle Performance Analysis", "Ride distance, vehicle demand and category performance"),
    "Revenue Analysis": ("Revenue & Business Insights", "Revenue trends, payment methods and top customers"),
    "Cancellation Analysis": ("Ride Cancellation Analysis", "Customer and driver cancellation patterns"),
    "Ratings Analysis": ("Customer & Driver Ratings", "Rating distribution and service quality analysis"),
}
title, subtitle = headers[page]

st.markdown(f'<div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


# ==============================================================================
# 1. OVERALL PAGE
# ==============================================================================
if page == "Overall":
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Total Bookings", fmt_plain(bookings))
    with c2: render_kpi("Success Rate", f"{success_rate:.2f}%")
    with c3: render_kpi("Total Revenue", fmt_money(revenue, 2))
    with c4: render_kpi("Successful Bookings", fmt_plain(successful))

    left_col, right_col = st.columns([1.18, 1])

    with left_col:
        st.markdown('<div class="chart-card"><div class="chart-title">Daily Ride Volume Trend</div>', unsafe_allow_html=True)
        daily = data.dropna(subset=["Date"]).groupby("Date_Only")["Booking_ID"].nunique().reset_index(name="Bookings")
        if not daily.empty:
            fig = px.line(daily, x="Date_Only", y="Bookings")
            fig.update_traces(
                line=dict(color=NAVY, width=2.5),
                fill="tozeroy",
                fillcolor="rgba(16, 39, 71, 0.08)"
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Total Bookings",
                xaxis=dict(tickformat="%d %b", dtick=7 * 86400000.0)
            )
            st.plotly_chart(chart_style(fig, 335), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="chart-card"><div class="chart-title">Booking Status Breakdown</div>', unsafe_allow_html=True)
        status_df = data["Booking_Status"].fillna("Unknown").value_counts().rename_axis("Status").reset_index(name="Bookings")
        status_colors = {
            "Success": YELLOW,
            "Canceled by Driver": NAVY,
            "Canceled by Customer": BLUE,
            "Driver Not Found": LIGHT_BLUE
        }
        total_st = status_df["Bookings"].sum()
        status_df["Label"] = status_df["Bookings"].map(lambda v: f"{fmt_k(v, 0)}<br>({v/total_st*100:.2f}%)")

        fig = px.pie(
            status_df,
            names="Status",
            values="Bookings",
            hole=0.58,
            color="Status",
            color_discrete_map=status_colors
        )
        # Dedicated domain prevents donut from colliding with the legend
        fig.update_traces(
            text=status_df["Label"],
            textinfo="text",
            textposition="outside",
            outsidetextfont=dict(size=11, color="#1E293B"),
            domain=dict(x=[0.02, 0.72]),
            rotation=60,
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        fig.update_layout(
            legend=dict(
                orientation="v",
                y=0.5,
                x=0.76,
                xanchor="left",
                yanchor="middle",
                title_text="Booking Status",
                font=dict(size=11)
            ),
            uniformtext=dict(minsize=10, mode="hide"),
            margin=dict(l=20, r=10, t=10, b=20),
            showlegend=True
        )
        st.plotly_chart(chart_style(fig, 335, show_legend=True), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Filters matching the Power BI report
    f_left, f_right = st.columns([1.18, 1])
    with f_left:
        st.markdown('<div class="filter-card"><div class="filter-title">Date</div>', unsafe_allow_html=True)
        all_dates = df["Date"].dropna()
        min_date, max_date = all_dates.min().date(), all_dates.max().date()
        date_sel = st.date_input(
            "Date range",
            value=st.session_state["filter_date"],
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
        if isinstance(date_sel, (tuple, list)) and len(date_sel) == 2:
            if date_sel != st.session_state["filter_date"]:
                st.session_state["filter_date"] = date_sel
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with f_right:
        st.markdown('<div class="filter-card"><div class="filter-title">Vehicle</div>', unsafe_allow_html=True)
        veh_opts = ["All"] + sorted(df["Vehicle_Type"].dropna().unique().tolist())
        veh_idx = veh_opts.index(st.session_state["filter_vehicle"]) if st.session_state["filter_vehicle"] in veh_opts else 0
        veh_sel = st.selectbox(
            "Vehicle filter",
            veh_opts,
            index=veh_idx,
            label_visibility="collapsed"
        )
        if veh_sel != st.session_state["filter_vehicle"]:
            st.session_state["filter_vehicle"] = veh_sel
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 2. VEHICLE ANALYSIS PAGE
# ==============================================================================
elif page == "Vehicle Analysis":
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Total Ride Distance (km)", fmt_k(distance, 2), label_at_bottom=True)
    with c2: render_kpi("Total Bookings", fmt_k(bookings, 0), label_at_bottom=True)
    with c3: render_kpi("Average Ride Distance (km)", f"{avg_distance:.2f}" if pd.notna(avg_distance) else "—", label_at_bottom=True)
    with c4: render_kpi("Vehicle Types", str(data["Vehicle_Type"].nunique()), label_at_bottom=True)

    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="chart-card"><div class="chart-title">Total Bookings by Vehicle Type</div>', unsafe_allow_html=True)
        bk_veh = data.groupby("Vehicle_Type")["Booking_ID"].nunique().reset_index(name="Bookings")
        desired_order = ["Prime Sedan", "E-Bike", "Auto", "Prime Plus", "Bike", "Prime SUV", "Mini"]
        bk_veh["Vehicle_Type"] = pd.Categorical(bk_veh["Vehicle_Type"], categories=desired_order, ordered=True)
        bk_veh = bk_veh.sort_values("Vehicle_Type").reset_index(drop=True)
        bk_veh["Label"] = bk_veh["Bookings"].map(lambda v: fmt_k(v, 0))

        fig = px.bar(
            bk_veh, x="Vehicle_Type", y="Bookings",
            color="Vehicle_Type", color_discrete_map=VEHICLE_COLORS,
            text="Label"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title="Vehicle Type", yaxis_title="Total Bookings")
        st.plotly_chart(chart_style(fig, 310), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="chart-card"><div class="chart-title">Total Ride Distance (km) by Vehicle Type</div>', unsafe_allow_html=True)
        dist_veh = data.groupby("Vehicle_Type")["Ride_Distance"].sum().sort_values(ascending=False).reset_index(name="Distance")
        dist_veh["Label"] = dist_veh["Distance"].map(lambda v: fmt_k(v, 2))

        fig = px.bar(
            dist_veh, x="Vehicle_Type", y="Distance",
            color="Vehicle_Type", color_discrete_map=VEHICLE_COLORS
        )
        fig.update_layout(
            xaxis_title="Vehicle Type",
            yaxis_title="Total Ride Distance (km)",
            yaxis=dict(tickformat=".1s")
        )
        st.plotly_chart(chart_style(fig, 310), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Average Customer Rating by Vehicle Type</div>', unsafe_allow_html=True)
    rate_veh = data.groupby("Vehicle_Type")["Customer_Rating"].mean().dropna().reset_index(name="Rating")
    veh_display_order = ["E-Bike", "Bike", "Mini", "Auto", "Prime SUV", "Prime Sedan", "Prime Plus"]
    rate_veh["Vehicle_Type"] = pd.Categorical(rate_veh["Vehicle_Type"], categories=veh_display_order, ordered=True)
    rate_veh = rate_veh.sort_values("Vehicle_Type").reset_index(drop=True)

    fig = px.bar(
        rate_veh, x="Rating", y="Vehicle_Type", orientation="h",
        color="Vehicle_Type", color_discrete_map=VEHICLE_COLORS
    )
    fig.update_layout(
        xaxis_title="Average Customer Rating",
        yaxis_title="Vehicle Type",
        xaxis_range=[0, 5],
        xaxis=dict(dtick=1)
    )
    st.plotly_chart(chart_style(fig, 290), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 3. REVENUE ANALYSIS PAGE
# ==============================================================================
elif page == "Revenue Analysis":
    customer_value = data["Booking_Value"].sum()
    avg_booking = data["Booking_Value"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Total Customer Booking Value", fmt_money(customer_value, 1), label_at_bottom=True)
    with c2: render_kpi("Total Success Revenue", fmt_money(revenue, 1), label_at_bottom=True)
    with c3: render_kpi("Average of Booking_Value", fmt_money(avg_booking, 1), label_at_bottom=True)
    with c4: render_kpi("Average Ride Distance (km)", f"{avg_distance:.2f}" if pd.notna(avg_distance) else "—", label_at_bottom=True)

    r_left, r_right = st.columns(2)

    with r_left:
        st.markdown('<div class="chart-card"><div class="chart-title">Revenue by Payment Method</div>', unsafe_allow_html=True)
        payment = success.dropna(subset=["Payment_Method"]).groupby("Payment_Method")["Booking_Value"].sum().reset_index(name="Revenue")
        tot_rev = payment["Revenue"].sum()

        # Clean non-overlapping formatted labels
        labels = []
        for v in payment["Revenue"]:
            pct = (v / tot_rev * 100)
            if pct < 2.0:
                labels.append(f"{fmt_k(v, 0)} ({pct:.1f}%)")
            else:
                labels.append(f"{fmt_k(v, 0)}<br>({pct:.2f}%)")
        payment["Label"] = labels

        fig = px.pie(
            payment, names="Payment_Method", values="Revenue", hole=0.55,
            color="Payment_Method", color_discrete_map=PAYMENT_COLORS
        )
        fig.update_traces(
            text=payment["Label"],
            textinfo="text",
            textposition="outside",
            outsidetextfont=dict(size=11, color="#1E293B"),
            domain=dict(x=[0.02, 0.72]),
            rotation=110,
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        fig.update_layout(
            legend=dict(
                title_text="Payment_Method",
                orientation="v",
                y=0.5,
                x=0.76,
                xanchor="left",
                yanchor="middle",
                font=dict(size=11)
            ),
            uniformtext=dict(minsize=10, mode="hide"),
            margin=dict(l=20, r=10, t=10, b=20),
            showlegend=True
        )
        st.plotly_chart(chart_style(fig, 335, show_legend=True), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_right:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 5 Customers by Revenue</div>', unsafe_allow_html=True)
        top5 = (success.groupby("Customer_ID")["Booking_Value"].sum()
                .nlargest(5).reset_index(name="Total Success Revenue"))
        top5 = top5.sort_values("Total Success Revenue", ascending=True).reset_index(drop=True)

        fig = px.bar(
            top5, x="Total Success Revenue", y="Customer_ID", orientation="h",
            color="Customer_ID", color_discrete_sequence=list(reversed(RANK_COLORS[:len(top5)]))
        )
        fig.update_layout(
            xaxis_title="Total Success Revenue",
            yaxis_title="Customer_ID",
            xaxis=dict(tickformat=".1s")
        )
        st.plotly_chart(chart_style(fig, 335), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Daily Ride Distance Trend</div>', unsafe_allow_html=True)
    daily_dist = data.dropna(subset=["Date"]).groupby("Date_Only")["Ride_Distance"].sum().reset_index(name="Distance")
    if not daily_dist.empty:
        fig = px.line(daily_dist, x="Date_Only", y="Distance")
        fig.update_traces(line=dict(color=NAVY, width=2.5))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Ride Distance (km)",
            xaxis=dict(tickformat="%d %b", dtick=7 * 86400000.0),
            yaxis=dict(tickformat=".0s")
        )
        st.plotly_chart(chart_style(fig, 270), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 4. CANCELLATION ANALYSIS PAGE
# ==============================================================================
elif page == "Cancellation Analysis":
    left_side, right_side = st.columns([1, 3.2])

    with left_side:
        render_kpi("Total Cancellations", fmt_k(cust_cancel_n + driver_cancel_n, 0), label_at_bottom=True)
        render_kpi("Total Incomplete Rides", fmt_k(incomplete, 0), label_at_bottom=True)
        render_kpi("Customer Cancellations", fmt_k(cust_cancel_n, 0), label_at_bottom=True)
        render_kpi("Driver Cancellations", fmt_k(driver_cancel_n, 0), label_at_bottom=True)

    with right_side:
        st.markdown('<div class="chart-card"><div class="chart-title">Driver Cancellation Reasons</div>', unsafe_allow_html=True)
        d_reasons = (data["Canceled_Rides_by_Driver"].dropna().astype(str).str.strip()
                     [~data["Canceled_Rides_by_Driver"].astype(str).str.lower().isin(["", "null", "none", "nan"])]
                     .value_counts().head(5).rename_axis("Reason").reset_index(name="Count"))
        d_reasons = d_reasons.sort_values("Count", ascending=True).reset_index(drop=True)

        fig = px.bar(
            d_reasons, x="Count", y="Reason", orientation="h",
            color="Reason", color_discrete_sequence=list(reversed(RANK_COLORS[:len(d_reasons)]))
        )
        fig.update_layout(
            xaxis_title="Count of Customer_ID",
            yaxis_title="Canceled_Rides_by_Driver",
            xaxis=dict(tickformat=".1s")
        )
        st.plotly_chart(chart_style(fig, 260), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Customer Cancellation Reasons</div>', unsafe_allow_html=True)
        c_reasons = (data["Canceled_Rides_by_Customer"].dropna().astype(str).str.strip()
                     [~data["Canceled_Rides_by_Customer"].astype(str).str.lower().isin(["", "null", "none", "nan"])]
                     .value_counts().head(5).rename_axis("Reason").reset_index(name="Count"))
        c_reasons = c_reasons.sort_values("Count", ascending=True).reset_index(drop=True)

        fig = px.bar(
            c_reasons, x="Count", y="Reason", orientation="h",
            color="Reason", color_discrete_sequence=list(reversed(RANK_COLORS[:len(c_reasons)]))
        )
        fig.update_layout(
            xaxis_title="Count of Booking_ID",
            yaxis_title="Canceled_Rides_by_Customer",
            xaxis=dict(tickformat=",d")
        )
        st.plotly_chart(chart_style(fig, 280), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 5. RATINGS ANALYSIS PAGE
# ==============================================================================
elif page == "Ratings Analysis":
    diff = avg_customer - avg_driver if pd.notna(avg_customer) and pd.notna(avg_driver) else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Total Bookings", fmt_k(bookings, 0), label_at_bottom=True)
    with c2: render_kpi("Average Customer Rating", f"{avg_customer:.2f}" if pd.notna(avg_customer) else "—", label_at_bottom=True)
    with c3: render_kpi("Average Driver Rating", f"{avg_driver:.2f}" if pd.notna(avg_driver) else "—", label_at_bottom=True)
    with c4: render_kpi("Rating Difference", f"{diff:.2f}", label_at_bottom=True)

    r_left, r_right = st.columns(2)

    with r_left:
        st.markdown('<div class="chart-card"><div class="chart-title">Customer Rating Distribution</div>', unsafe_allow_html=True)
        c_counts = (data["Customer_Rating"].dropna().round(1).value_counts().sort_index()
                    .rename_axis("Rating").reset_index(name="Count"))
        fig = px.bar(c_counts, x="Count", y="Rating", orientation="h", color_discrete_sequence=[YELLOW])
        fig.update_layout(
            xaxis_title="Count of Customer_ID",
            yaxis_title="Customer_Rating",
            xaxis=dict(tickformat=".1s"),
            yaxis=dict(dtick=1, range=[2.8, 5.2])
        )
        st.plotly_chart(chart_style(fig, 290), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_right:
        st.markdown('<div class="chart-card"><div class="chart-title">Driver Rating Distribution</div>', unsafe_allow_html=True)
        d_counts = (data["Driver_Ratings"].dropna().round(1).value_counts().sort_index()
                    .rename_axis("Rating").reset_index(name="Count"))
        fig = px.bar(d_counts, x="Count", y="Rating", orientation="h", color_discrete_sequence=[NAVY])
        fig.update_layout(
            xaxis_title="Count of Customer_ID",
            yaxis_title="Driver_Ratings",
            xaxis=dict(tickformat=".1s"),
            yaxis=dict(dtick=1, range=[2.8, 5.2])
        )
        st.plotly_chart(chart_style(fig, 290), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Customer vs Driver Ratings by Vehicle Type</div>', unsafe_allow_html=True)
    comp = data.groupby("Vehicle_Type")[["Customer_Rating", "Driver_Ratings"]].mean().reset_index()
    comp_order = ["Prime Plus", "Prime Sedan", "Prime SUV", "Auto", "Mini", "Bike", "E-Bike"]
    comp["Vehicle_Type"] = pd.Categorical(comp["Vehicle_Type"], categories=comp_order, ordered=True)
    comp = comp.sort_values("Vehicle_Type").reset_index(drop=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=comp["Vehicle_Type"],
        y=comp["Customer_Rating"],
        name="Average Customer Rating",
        marker_color=YELLOW
    ))
    fig.add_trace(go.Bar(
        x=comp["Vehicle_Type"],
        y=comp["Driver_Ratings"],
        name="Average Driver Rating",
        marker_color=NAVY
    ))
    fig.update_layout(
        barmode="group",
        xaxis_title="Vehicle Type",
        yaxis_title="Average Customer Rating",
        yaxis=dict(range=[0, 5], dtick=5),
        legend=dict(orientation="h", y=1.14, x=0, title_text="")
    )
    st.plotly_chart(chart_style(fig, 300, show_legend=True), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)