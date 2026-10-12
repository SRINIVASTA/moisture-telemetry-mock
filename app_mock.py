import streamlit as st
import pandas as pd
import time
import math
import os
import paho.mqtt.client as mqtt

# Set widescreen layout
st.set_page_config(page_title="Telemetry Core - Custom Thresholds", layout="wide")

st.markdown("""
    <style>
    .telemetry-title { text-align: center; font-family: 'Courier New', monospace; font-weight: bold; color: #00FF66; }
    </style>
    <h1 class='telemetry-title'>🛰️ TELEMETRY SYSTEM CORE (DYNAMIC CONTROL)</h1>
    """, unsafe_allow_html=True)

CSV_FILE = "telemetry_log.csv"

# 1. Initialize State Metrics
if "history" not in st.session_state:
    st.session_state.history = []
if "sim_tick" not in st.session_state:
    st.session_state.sim_tick = 0
if "watering_active" not in st.session_state:
    st.session_state.watering_active = False
if "cloud_moisture" not in st.session_state:
    st.session_state.cloud_moisture = 45

# 2. MQTT Cloud Signal Broker (FIXED: Perfectly matches the Wokwi server pipeline address)
def on_message(client, userdata, message):
    try:
        # Decode the live moisture percentage numbers passing over the internet
        st.session_state.cloud_moisture = int(message.payload.decode("utf-8"))
    except Exception:
        pass

if "mqtt_initialized" not in st.session_state:
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.on_message = on_message
        # FIXED: Added the complete, clear broker address string
        mqtt_client.connect("://hivemq.com", 1883, 60)
        mqtt_client.subscribe("sfic2026/krishitwin/moisture")
        mqtt_client.loop_start() # Launches real-time background tracking threads
        st.session_state.mqtt_initialized = True
    except Exception as e:
        st.sidebar.error(f"⚠️ Cloud sync issue: {e}")

# 3. Operations Panel Layout (Houses Controls and GitHub Link)
with st.sidebar:
    st.header("🎮 System Operations")
    run_simulation = st.toggle("🔌 Activate Telemetry Stream", value=False)
    
    if st.button("🗑️ Clear Log & Reset History", type="primary"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        st.session_state.history = []
        st.session_state.sim_tick = 0
        st.session_state.watering_active = False
        st.toast("Telemetry logs cleared!", icon="🔥")
        st.rerun()

    st.markdown("---")
    st.header("📂 Code Repository")
    github_repo_link = "https://github.com"
    st.markdown(f"📂 **[View ECE Blueprints (GitHub)]({github_repo_link})**")
    
    st.markdown("---")
    st.header("⚙️ Threshold Controls")
    st.write("Adjust automated trigger points dynamically:")
    dry_threshold = st.slider("⚠️ Dry Start Threshold (%)", 5, 40, 20, 1)
    wet_threshold = st.slider("🛑 Wet Stop Threshold (%)", 60, 95, 80, 1)
    
    st.markdown("---")
    st.header("💾 Storage Manager")
    download_spot = st.empty()

# 4. Main Layout Grid Components (Split Screen: Left for Telemetry, Right for Wokwi Board)
alert_banner = st.empty()
left_pane, right_pane = st.columns(2)

with left_pane:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Current Node")
        metric_spot = st.empty()
    with col2:
        st.subheader("⚡ System Diagnostics")
        status_spot = st.empty()
        
    st.subheader("📈 Real-Time Stream Timeline")
    chart_spot = st.empty()

with right_pane:
    st.subheader("🔌 Interactive ECE Hardware Node")
    # FIXED: Embedded your exact Wokwi canvas link directly
    wokwi_embed_url = "https://wokwi.com/projects/477695135339057153"
    st.components.v1.iframe(wokwi_embed_url, height=450, scrolling=False)

st.subheader("📋 Live Log Terminal (Last 10 Rows)")
table_spot = st.empty()

def render_display_state(live_reading, sys_state, metric_delta, color_mode, total_rows, df_chart, last_10_df):
    with metric_spot.container():
        st.metric(label="VIRTUAL_ECE_NODE_01", value=f"{live_reading} %", delta=metric_delta, delta_color=color_mode)
    with status_spot.container():
        st.code(f"Telemetry Mode : MQTT_CLOUD_STREAM\nActive State   : {sys_state}\nDry Trigger Set: {dry_threshold}%\nWet Trigger Set: {wet_threshold}%\nTotal Database : {total_rows} rows saved", language="yaml")
    with chart_spot.container():
        if not df_chart.empty: 
            st.line_chart(df_chart.set_index("System Time"), height=230)
        else: 
            st.info("No timeline data loaded.")
    with table_spot.container():
        st.dataframe(last_10_df, use_container_width=True)

all_data_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
all_data_df = pd.read_csv(CSV_FILE) if all_data_exists else pd.DataFrame(columns=["Timestamp", "Moisture (%)", "State", "Dry_Limit_Set", "Wet_Limit_Set"])
total_accumulated_rows = len(all_data_df)
last_10_df = all_data_df.tail(10).iloc[::-1] if not all_data_df.empty else all_data_df
df_chart = pd.DataFrame(st.session_state.history)

if not run_simulation:
    alert_banner.info("⏸️ TELEMETRY SYSTEM IDLE: Click the play button inside the hardware node on the right, then toggle the sidebar switch to sync live data.")
    render_display_state(st.session_state.cloud_moisture, "IDLE / SUSPENDED", "🚫 PAUSED", "off", total_accumulated_rows, df_chart, last_10_df)

# 5. Live Runtime Pipeline Loop
while run_simulation:
    st.session_state.sim_tick += 1
    t = st.session_state.sim_tick
    
    # Capture live telemetry values arriving straight over the cloud network bridge
    live_reading = st.session_state.cloud_moisture

    if live_reading <= dry_threshold:
        sys_state = "CRITICAL: DRY START"
        alert_banner.error(f"🚨 STATE: [{sys_state}] - Soil below safe threshold ({dry_threshold}%). Water Pump ON.")
        metric_delta = f"- BELOW {dry_threshold}%"
        color_mode = "inverse"
        st.session_state.watering_active = True
    elif live_reading >= wet_threshold:
        sys_state = "CRITICAL: WET STOP"
        alert_banner.warning(f"🛑 STATE: [{sys_state}] - Soil reached ceiling threshold ({wet_threshold}%). Water Pump OFF.")
        metric_delta = f"+ ABOVE {wet_threshold}%"
        color_mode = "normal"
        st.session_state.watering_active = False
    else:
        sys_state = "PUMP ACTIVE" if st.session_state.watering_active else "NOMINAL OPERATION"
        alert_banner.success(f"✅ TELEMETRY LINK SYNCED: [{sys_state}]")
        metric_delta = "🌊 INCREASING" if st.session_state.watering_active else "🍂 DECREASING"
        color_mode = "off"

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    new_row_df = pd.DataFrame([{"Timestamp": timestamp, "Moisture (%)": live_reading, "State": sys_state, "Dry_Limit_Set": dry_threshold, "Wet_Limit_Set": wet_threshold}])
    if not os.path.exists(CSV_FILE):
        new_row_df.to_csv(CSV_FILE, index=False)
    else:
        new_row_df.to_csv(CSV_FILE, mode='a', header=False, index=False)

    st.session_state.history.append({"System Time": time.strftime('%H:%M:%S'), "Moisture (%)": live_reading})
    if len(st.session_state.history) > 30: 
        st.session_state.history.pop(0)
    df_chart = pd.DataFrame(st.session_state.history)

    all_data_df = pd.read_csv(CSV_FILE)
    last_10_df = all_data_df.tail(10).iloc[::-1)
    total_accumulated_rows = len(all_data_df)

    render_display_state(live_reading, sys_state, metric_delta, color_mode, total_accumulated_rows, df_chart, last_10_df)

    if len(all_data_df) > 0:
        csv_data = all_data_df.to_csv(index=False).encode('utf-8')
        with download_spot.container():
            st.download_button(label="📥 Download Complete CSV Log", data=csv_data, file_name=f"telemetry_export_{time.strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", key=f"csv_download_btn_{t}")
        
    time.sleep(1)
    st.rerun()
