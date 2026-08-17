import streamlit as st
import pandas as pd
import time
import math

# Set widescreen telemetry dashboard layout
st.set_page_config(page_title="Telemetry Core - Mock Setup", layout="wide")

# Custom styling for a dark industrial telemetry theme
st.markdown("""
    <style>
    .telemetry-title { text-align: center; font-family: 'Courier New', monospace; font-weight: bold; color: #00FF66; }
    </style>
    <h1 class='telemetry-title'>🛰️ TELEMETRY SYSTEM CORE (MOCK MODE)</h1>
    """, unsafe_allow_html=True)

# 1. Initialize Mock Simulation Variables in Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "sim_tick" not in st.session_state:
    st.session_state.sim_tick = 0
if "watering_active" not in st.session_state:
    st.session_state.watering_active = False

# 2. Layout Grid Structure for Telemetry Telecast
alert_banner = st.empty()
col1, col2, col3 = st.columns([1, 1, 2]) # Makes the chart column wider

with col1:
    st.subheader("📊 Current Node")
    metric_spot = st.empty()

with col2:
    st.subheader("⚡ System Diagnostics")
    status_spot = st.empty()

with col3:
    st.subheader("📈 Real-Time Stream Timeline")
    chart_spot = st.empty()

# 3. Telemetry Live Mock Loop
while True:
    st.session_state.sim_tick += 1
    t = st.session_state.sim_tick
    
    # --- MOISTURE SIMULATION LOGIC ---
    # This math fakes natural drying out and rapid watering spikes over time
    if st.session_state.watering_active:
        # Rapidly increase moisture during watering phase
        last_moisture = st.session_state.history[-1]["Moisture (%)"] if st.session_state.history else 35
        live_reading = min(100, last_moisture + int(math.sin(t) * 5) + 12)
    else:
        # Gradually decrease moisture during dry-down phase
        last_moisture = st.session_state.history[-1]["Moisture (%)"] if st.session_state.history else 60
        live_reading = max(0, last_moisture - int(math.cos(t) * 2) - 3)

    # --- STATE MATRIX PROCESSING ---
    if live_reading <= 20:
        sys_state = "CRITICAL: DRY START"
        alert_banner.error(f"🚨 SYSTEM CRITICAL STATE TRIGGERED: [{sys_state}] - Soil is parched. Activating irrigation pump...")
        metric_delta = "- CRITICAL LOW"
        color_mode = "inverse"
        st.session_state.watering_active = True  # Auto-start watering when dry
        
    elif live_reading >= 80:
        sys_state = "CRITICAL: WET STOP"
        alert_banner.warning(f"🛑 AUTOMATED CONTROL INTERVENTION: [{sys_state}] - Soil saturated. Shutting down pump.")
        metric_delta = "+ SATURATION LIMIT"
        color_mode = "normal"
        st.session_state.watering_active = False # Auto-stop watering when saturated
        
    else:
        if st.session_state.watering_active:
            sys_state = "PUMP ACTIVE - WATERING IN PROGRESS"
            alert_banner.info(f"💦 SYSTEM STATUS: [{sys_state}] - Filling grid reservoir.")
            metric_delta = "🌊 INCREASING"
            color_mode = "off"
        else:
            sys_state = "NOMINAL OPERATION - NATURAL DRYING"
            alert_banner.success(f"✅ TELEMETRY LINK HEALTHY: [{sys_state}]")
            metric_delta = "🍂 DECREASING"
            color_mode = "off"

    # --- STREAM LOGGING ARRAY MANAGEMENT ---
    timestamp = time.strftime('%H:%M:%S')
    st.session_state.history.append({"System Time": timestamp, "Moisture (%)": live_reading})
    
    # Limit chart memory viewport window to the last 30 intervals
    if len(st.session_state.history) > 30:
        st.session_state.history.pop(0)
        
    df = pd.DataFrame(st.session_state.history)

    # --- PUSH LIVE METRICS TO DISPLAY ---
    with metric_spot.container():
        st.metric(
            label="MOCK_SENSOR_NODE_01", 
            value=f"{live_reading} %", 
            delta=metric_delta, 
            delta_color=color_mode
        )
        
    with status_spot.container():
        pump_status = "ON (Streaming Water)" if st.session_state.watering_active else "OFF (Closed Valve)"
        st.code(f"""
Telemetry Mode: MOCK_SIMULATOR
Active State  : {sys_state}
Relay Switch  : {pump_status}
Packet Clock  : {t} cycles
Min Window Val: {df['Moisture (%)'].min()}%
Max Window Val: {df['Moisture (%)'].max()}%
        """, language="yaml")
        
    with chart_spot.container():
        st.line_chart(df.set_index("System Time"), height=280)
        
    # Screen refresh stream tick rate (approx 1 second for snappy testing)
    time.sleep(1)
