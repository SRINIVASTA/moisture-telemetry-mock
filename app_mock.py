import streamlit as st
import pandas as pd
import time
import math
import os

# Set widescreen layout
st.set_page_config(page_title="Telemetry Core - Custom Thresholds", layout="wide")

st.markdown("""
    <style>
    .telemetry-title { text-align: center; font-family: 'Courier New', monospace; font-weight: bold; color: #00FF66; }
    </style>
    <h1 class='telemetry-title'>🛰️ TELEMETRY SYSTEM CORE (DYNAMIC CONTROL)</h1>
    """, unsafe_allow_html=True)

CSV_FILE = "telemetry_log.csv"

# 1. Initialize Mock States
if "history" not in st.session_state:
    st.session_state.history = []
if "sim_tick" not in st.session_state:
    st.session_state.sim_tick = 0
if "watering_active" not in st.session_state:
    st.session_state.watering_active = False

# 2. Sidebar Configuration (Houses Sliders and Download Button)
with st.sidebar:
    st.header("⚙️ Threshold Controls")
    st.write("Adjust trigger boundaries in real time:")
    
    # Live sliders to change logic rules on the fly
    dry_threshold = st.slider(
        label="⚠️ Dry Start Threshold (%)", 
        min_value=5, 
        max_value=40, 
        value=20, 
        step=1
    )
    
    wet_threshold = st.slider(
        label="🛑 Wet Stop Threshold (%)", 
        min_value=60, 
        max_value=95, 
        value=80, 
        step=1
    )
    
    st.markdown("---")
    st.header("💾 Storage Manager")
    download_spot = st.empty()

# 3. Main Layout Grid Components
alert_banner = st.empty()
col1, col2, col3 = st.columns()

with col1:
    st.subheader("📊 Current Node")
    metric_spot = st.empty()

with col2:
    st.subheader("⚡ System Diagnostics")
    status_spot = st.empty()

with col3:
    st.subheader("📈 Real-Time Stream Timeline")
    chart_spot = st.empty()

st.subheader("📋 Live Log Terminal (Last 10 Accumulated Rows)")
table_spot = st.empty()

# 4. Infinite Telemetry Pipeline Loop
while True:
    st.session_state.sim_tick += 1
    t = st.session_state.sim_tick
    
    # --- MOISTURE SIMULATION LOGIC ---
    if st.session_state.watering_active:
        last_moisture = st.session_state.history[-1]["Moisture (%)"] if st.session_state.history else 35
        live_reading = min(100, last_moisture + int(math.sin(t) * 5) + 12)
    else:
        last_moisture = st.session_state.history[-1]["Moisture (%)"] if st.session_state.history else 60
        live_reading = max(0, last_moisture - int(math.cos(t) * 2) - 3)

    # --- STATE PROCESSING MATRIX (USES SLIDER VARIABLES) ---
    if live_reading <= dry_threshold:
        sys_state = "CRITICAL: DRY START"
        alert_banner.error(f"🚨 STATE: [{sys_state}] - Soil below configured safe limit ({dry_threshold}%). Pump ON.")
        metric_delta = f"- BELOW {dry_threshold}%"
        color_mode = "inverse"
        st.session_state.watering_active = True
        
    elif live_reading >= wet_threshold:
        sys_state = "CRITICAL: WET STOP"
        alert_banner.warning(f"🛑 STATE: [{sys_state}] - Soil reached ceiling boundary ({wet_threshold}%). Pump OFF.")
        metric_delta = f"+ ABOVE {wet_threshold}%"
        color_mode = "normal"
        st.session_state.watering_active = False
        
    else:
        sys_state = "PUMP ACTIVE" if st.session_state.watering_active else "NOMINAL OPERATION"
        alert_banner.success(f"✅ TELEMETRY LINK ACTIVE: [{sys_state}]")
        metric_delta = "🌊 INCREASING" if st.session_state.watering_active else "🍂 DECREASING"
        color_mode = "off"

    # --- SAVE PAYLOAD TO DISK DATABASE ---
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    new_data = {
        "Timestamp": timestamp, 
        "Moisture (%)": live_reading, 
        "State": sys_state,
        "Dry_Limit_Set": dry_threshold,
        "Wet_Limit_Set": wet_threshold
    }
    new_row_df = pd.DataFrame([new_data])
    
    if not os.path.exists(CSV_FILE):
        new_row_df.to_csv(CSV_FILE, index=False)
    else:
        new_row_df.to_csv(CSV_FILE, mode='a', header=False, index=False)

    # --- PROCESS CHART MEMORY WINDOW ---
    st.session_state.history.append({"System Time": time.strftime('%H:%M:%S'), "Moisture (%)": live_reading})
    if len(st.session_state.history) > 30:
        st.session_state.history.pop(0)
    df_chart = pd.DataFrame(st.session_state.history)

    # --- READ COMPLETE DATASET AND SLICE LAST 10 ROWS ---
    all_data_df = pd.read_csv(CSV_FILE)
    last_10_df = all_data_df.tail(10).iloc[::-1]
    total_accumulated_rows = len(all_data_df)

    # --- RENDER TELEMETRY PLUGINS ---
    with metric_spot.container():
        st.metric(label="MOCK_SENSOR_NODE_01", value=f"{live_reading} %", delta=metric_delta, delta_color=color_mode)
        
    with status_spot.container():
        st.code(f"""
Telemetry Mode : MOCK_SIMULATOR
Active State   : {sys_state}
Dry Trigger Set: {dry_threshold}%
Wet Trigger Set: {wet_threshold}%
Total Database : {total_accumulated_rows} rows saved
        """, language="yaml")
        
    with chart_spot.container():
        st.line_chart(df_chart.set_index("System Time"), height=230)
        
    with table_spot.container():
        st.dataframe(last_10_df, use_container_width=True)

    # --- CONVERT COMPLETE LOG FOR DOWNLOAD LINK ---
    csv_data = all_data_df.to_csv(index=False).encode('utf-8')
    with download_spot.container():
        st.download_button(
            label="📥 Download Complete CSV Log",
            data=csv_data,
            file_name=f"telemetry_export_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="csv_download_btn"
        )
        
    # Execution clock rate interval (1 second)
    time.sleep(1)
