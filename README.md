🌦️ AI Weather Summariser

Real-time AI-generated weather updates powered by Groq Llama & Open-Meteo

The AI Weather Summariser is a lightweight agent that continuously monitors the weather for any location and generates natural, human-like summaries using Groq’s Llama model.
It automatically detects changes in temperature, wind, humidity, or precipitation and prints a fresh summary instantly.

No OpenWeather API required — uses Open-Meteo (free, no key) and Groq Llama for the summary.


🚀 Features
✔️ AI-Powered Summaries
Uses Groq Llama-3 to generate clean, short weather reports.
Produces 1–3 sentence natural summaries.

✔️ Real-Time Weather Updates
Continuously polls the Open-Meteo API.
Generates a new summary only when weather changes.

✔️ Efficient Change Detection
Watches humidity, temperature, precipitation & wind.
Avoids repetitive output — only prints updates.

✔️ Simple CLI Agent
Run with one command.
No browser, no excess UI, just clean terminal output.


🧠 How It Works
You provide a location name (e.g., "Bengaluru").

The script fetches:
Geo-coordinates (via Nominatim)
Real-time weather (via Open-Meteo)

The weather data is turned into a prompt.

Groq’s Llama model generates a human-like summary.

A background loop keeps checking for changes and updates output.


🛠️ Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-weather-summariser.git
cd ai-weather-summariser

2. Install dependencies
pip install -r requirements.txt

3. Add your Groq API Key

Create a .env file:

GROQ_API_KEY=your_groq_key_here


▶️ Usage

Run the weather agent:

python weather_agent.py


By default, it monitors Bengaluru.
You can edit the file to change the default location or modify the main function:

run_weather_agent("New York")

📌 Example Output
🌦 Weather Update:
Cloudy skies over Bengaluru with mild temperatures and light winds. No rainfall expected for now.
-----------------------


📁 Project Structure
📦 ai-weather-summariser
 ┣ 📜 weather_agent.py
 ┣ 📜 requirements.txt
 ┗ 📜 README.md


🌐 APIs Used
Open-Meteo
Free, fast, no API key required
Provides real-time global weather

Groq Llama-3
Ultra-fast inference
Generates human-like summaries

📄 License
MIT Lisence


💡 Future Improvements
TTS weather voice assistant
Web dashboard
Push notifications
Multi-location monitoring
Integrate with smart-home devices


⭐ Support & Contribution

Feel free to:
⭐ Star the repo
🐛 Report issues
🛠️ Submit PRs
💬 Suggest new features
