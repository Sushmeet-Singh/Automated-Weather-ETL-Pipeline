# Automated-Weather-ETL-Pipeline
Automated weather ETL pipeline that collects, processes, and visualizes real-time data from multiple global cities using Python, PostgreSQL, and Streamlit.
# 🌦️ Automated Weather ETL Pipeline

## 📌 Overview
This project implements a fully automated ETL pipeline that collects, processes, and visualizes real-time weather data across multiple global cities.

The system runs continuously, fetching data every 15 minutes, transforming it, and storing it in a PostgreSQL database. The processed data is then displayed through an interactive Streamlit dashboard.

---

## 🎯 Objective
To design and build a scalable, end-to-end data pipeline that simulates real-world data engineering workflows, including automation, validation, storage, and visualization.

---

## 💼 Business Relevance
Weather data plays a key role in operational decision-making across industries such as logistics, travel, and retail.

This pipeline demonstrates how real-time, location-specific insights can support:
- Demand forecasting  
- Route and delivery optimization  
- Operational planning across regions  

---

## ⚙️ Tech Stack
- **API:** OpenWeatherMap  
- **Programming Language:** Python  
- **Scheduler:** APScheduler  
- **Database:** PostgreSQL  
- **Visualization:** Streamlit, Plotly  

---

## 🔄 Pipeline Architecture

### 1. Data Extraction
- Fetches live weather data using OpenWeatherMap API  
- Covers 15 cities across 6 continents  
- Runs automatically every 15 minutes  

### 2. Data Transformation
- Validates incoming data  
- Standardizes formats and units  
- Prepares features for analysis  

### 3. Data Loading
- Stores processed data in PostgreSQL  
- Ensures structured and query-ready storage  

### 4. Data Visualization
- Interactive dashboard built with Streamlit  
- Real-time updates using Plotly charts  

---

## 📊 Dashboard Features
- Dynamic city selection  
- Multiple weather metrics (temperature, humidity, wind, pressure)  
- “Feels like” vs actual temperature comparison  
- Configurable display for multiple cities  

---

## 🚀 Future Enhancements
- Containerization using Docker  
- Cloud deployment (AWS/GCP/Azure)  
- Pipeline monitoring and alerting  
- Historical trend analysis and forecasting  

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.x  
- PostgreSQL  
- OpenWeatherMap API key  

### Installation
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

## Configuration
Add your OpenWeatherMap API key
Configure PostgreSQL connection settings

## Run the Pipeline
python main.py


## Run the Dashboard
streamlit run app.py
