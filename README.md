🌦️ AI Weather Summariser

Real-time, AI-powered weather updates using Open-Meteo + Groq Llama



⭐ Overview
AI Weather Summariser is a lightweight Python script that continuously monitors live weather conditions for any location and generates human-like, concise summaries using Groq’s LLaMA model.
It detects changes in weather and prints a new summary only when the weather updates, making it perfect for terminals, dashboards, automation, and IoT setups.



🚫 No OpenWeather API used
🛰️ Open-Meteo for real-time weather data
🧠 Groq LLaMA for AI-generated summaries
⏳ Continuous monitoring loop



✨ Features
Input by place name (e.g., "Bengaluru, India")
Input by coordinates (lat,lon)
Uses Nominatim for geocoding (OpenStreetMap)
Uses Open-Meteo (no API key required)
Generates short weather summaries only
Detects weather changes by computing a “weather fingerprint”
Prints updated summary only when weather changes
Supports configurable polling interval
Pure Python. Lightweight. No unnecessary dependencies.



📁 File: ai_weather_summariser.py

This script includes:

Geocoding

Real-time weather fetching

LLaMA prompt engineering for concise summaries

Intelligent weather-change detection

Live monitoring loop



🛠️ Installation
1. Clone the repository:
git clone https://github.com/thrivexlab/Weather_Summariser_v1/
cd Weather_Summariser_v1/

2. Install dependencies:
pip install groq requests python-dotenv

3. Set your Groq API key:

Create .env:

GroqAPIKey=your_api_key_here


or export manually:

export GroqAPIKey=your_api_key_here



🚀 Usage
Monitor weather by place name
python ai_weather_summariser.py --place "Bengaluru, India"

Monitor by coordinates
python ai_weather_summariser.py --coords "12.9716,77.5946"

Change polling interval (default: 60 sec)
python ai_weather_summariser.py --place "Mumbai" --poll 30

Use a different Groq model
python ai_weather_summariser.py --place "Delhi" --model llama-3.1-8b-instant



🧠 How It Works
1. Geocoding

Converts place name → latitude, longitude (via Nominatim)

2. Fetch Weather

Uses Open-Meteo to retrieve current_weather + hourly fields

3. Generate AI Summary

Sends a structured JSON snapshot to Groq LLaMA

LLaMA returns 1–3 sentence concise weather summary

4. Smart Change Detection

Weather fingerprint includes:

Temperature

Wind

Humidity

Precipitation

Weather code

If fingerprint changes → print new summary.



📌 Example Output
Mostly cloudy in Bengaluru with 21°C temperature and light winds. No rainfall expected for now.



🧩 Arguments
Argument	Description
--place	Place name (string)
--coords	Coordinates in lat,lon format
--poll	Polling interval in seconds
--model	Groq model name



📜 Environment Variables
Variable	Purpose
GroqAPIKey	Required Groq API key


🛡️ Notes
Nominatim requires a User-Agent (handled in script)
Open-Meteo is free and needs no API key
Poll responsibly to avoid rate limits



🤝 Contributing
Pull requests are welcome!
Feel free to open issues for new features or improvements.

📄 License
MIT License

⭐ Support the Project
If you like this project, star the repo ⭐ on GitHub!
