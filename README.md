# 🛰️ Telemetry System Core (Dynamic Control)

A real-time, interactive IoT telemetry simulation dashboard built with **Streamlit** and **Pandas**. This application simulates smart agriculture soil moisture tracking, automatically triggering water pump logic based on dynamic, user-controlled threshold barriers.

---

## 🚀 Key Features

* **Real-Time Data Pipeline**: Simulated live loop mimicking incoming physical node hardware packages.
* **Dynamic Controls**: Live sidebar sliders to manipulate safe boundary thresholds (`Dry Start` / `Wet Stop`) on the fly.
* **Wiped State Control**: Clean toggle to halt the data stream alongside a hard reset button to instantly clear accumulated logs.
* **Local CSV Persistence**: Automatic tracking mechanism saves historical timelines directly to a local disk storage matrix (`telemetry_log.csv`).
* **Hot Data Export**: Complete dynamic data download option available directly inside the layout canvas.

---

## 🛠️ System Architecture & Mechanics
---
graph TD
    %% Main Node
    UI["🛰️ Streamlit Web Interface"] --> Control["⚙️ Sidebar Logs & Controls"]
    UI --> Engine["⚡ Stream Loop (1Hz Engine)"]

    %% Sidebar Actions
    Control --> Reset["🗑️ Clear/Reset Action"]
    Reset --> DiskWipe["🔥 Delete CSV from Disk"]

    %% Stream Processing Actions
    Engine --> State["🧠 State Processing Engine"]
    State --> Append["📝 Append Data Array"]
    Append --> Save["💾 Save to Disk (CSV Log)"]

    %% Styling and coloring for better visual hierarchy
    style UI fill:#00ff66,stroke:#333,stroke-width:2px,color:#000
    style Engine fill:#17a2b8,stroke:#333,stroke-width:1px,color:#fff
    style Control fill:#ffc107,stroke:#333,stroke-width:1px,color:#000
    style DiskWipe fill:#dc3545,stroke:#333,stroke-width:1px,color:#fff
    style Save fill:#28a745,stroke:#333,stroke-width:1px,color:#fff
---

1. **State Machine Logic**:
   * **`Moisture <= Dry Threshold`**: Triggers a `CRITICAL: DRY START` alert status and switches the pump infrastructure **ON**.
   * **`Moisture >= Wet Threshold`**: Triggers a `CRITICAL: WET STOP` warning safety threshold and switches the pump infrastructure **OFF**.
   * **`In-Between Zones`**: Runs nominal operational protocols depending on the prior context state.

2. **Session Persistence**: Utilizes `st.session_state` to retain live system metrics, tick indexes, and moving chart windows without breaking script execution layers.

---

## 📦 Installation & Setup

### Prerequisites
Make sure you have Python 3.8+ installed on your computer.

### 1. Clone or Copy the Script
Create a local project directory and place the application script inside it named as `app.py`.

### 2. Install Required Packages
Run the following installation command in your terminal terminal pipeline to gather the tracking dependencies:
```bash
pip install streamlit pandas
```

### 3. Initialize the Core Application
Launch the local web server matrix using the core Streamlit CLI command:
```bash
streamlit run app.py
```

---

## 🎮 Interface Controls Guide

* **Activate Telemetry Stream (Toggle)**: Flip this to turn on the live 1-second interval execution loop. Switch it off at any time to pause monitoring.
* **Clear Log & Reset History (Button)**: Deletes the permanent `telemetry_log.csv` file from disk and wipes the visual charts cleanly.
* **Threshold Sliders**: Change the triggers dynamically to test sensor alerts instantly without resetting your progress.

---

## 📁 Data Storage Layout
The log pipeline saves structured tabular events to `telemetry_log.csv` matching this architecture schema:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Timestamp** | `String` | System clock reference (`YYYY-MM-DD HH:MM:SS`) |
| **Moisture (%)** | `Integer` | Computed mock soil moisture metrics |
| **State** | `String` | Operational system warning code status |
| **Dry_Limit_Set**| `Integer` | Active lower safe threshold boundary configuration |
| **Wet_Limit_Set**| `Integer` | Active upper ceiling limit boundary configuration |
