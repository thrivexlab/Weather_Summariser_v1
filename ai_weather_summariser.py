import os
import time
import json
import requests
from typing import Tuple, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Config
GROQ_API_KEY = os.getenv("GroqAPIKey")
if not GROQ_API_KEY:
    raise RuntimeError("Please set GROQ_API_KEY in environment variables.")

# Nominatim requires a descriptive User-Agent
USER_AGENT = "AIWeatherSummary/1.0 (example@example.com) - example usage"

# Polling interval in seconds (change to suit). For production be careful with rate limits.
POLL_INTERVAL = 60  # seconds

# Open-Meteo endpoint template
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def geocode_place(place: str) -> Optional[Tuple[float, float, str]]:
    """Forward geocode a place name to (lat, lon, display_name) using Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    item = data[0]
    lat = float(item["lat"])
    lon = float(item["lon"])
    display_name = item.get("display_name", place)
    return lat, lon, display_name


def fetch_current_weather(lat: float, lon: float, timezone: str = "auto") -> dict:
    """Fetch current weather + some hourly fields from Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        # include hourly fields that can help summarization:
        "hourly": "temperature_2m,relativehumidity_2m,precipitation,weathercode,windspeed_10m",
        "timezone": timezone,
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def brief_weather_prompt(location_name: str, weather_json: dict) -> str:
    """Construct the prompt for the LLM to create a concise summary only."""
    current = weather_json.get("current_weather", {})
    # Basic fields
    temp = current.get("temperature")
    windspeed = current.get("windspeed")
    winddir = current.get("winddirection")
    weather_time = current.get("time")
    # also include latest hourly datapoint for precipitation if available
    # (Open-Meteo returns hourly arrays; we'll pick the latest index if possible)
    hourly = weather_json.get("hourly", {})
    # get last values if present (best-effort)
    last_idx = None
    if "time" in hourly:
        last_idx = len(hourly["time"]) - 1
    humidity = None
    precipitation = None
    weathercode = None
    if last_idx is not None:
        humidity = hourly.get("relativehumidity_2m", [None])[last_idx]
        precipitation = hourly.get("precipitation", [None])[last_idx]
        weathercode = hourly.get("weathercode", [None])[last_idx]

    # Build prompt instructing Llama to output ONLY the summary, short and precise
    prompt = f"""
You are a concise weather summariser. OUTPUT ONLY A SHORT SUMMARY (no extra text, no bullet points, no commentary)
in 1-3 sentences describing the current weather in {location_name} as of {weather_time}.
Include temperature (°C), wind speed (m/s or km/h), and any precipitation or notable conditions.
If precipitation is occurring or imminent, mention it clearly. Keep it direct and factual.

JSON data:
{json.dumps({"temperature": temp,
             "windspeed": windspeed,
             "winddirection": winddir,
             "relative_humidity": humidity,
             "precipitation": precipitation,
             "weathercode": weathercode,
             "time": weather_time}, default=str, indent=2)}
"""
    return prompt.strip()


def ask_groq_for_summary(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Calls Groq Chat Completion and returns the model's textual content.
    """
    messages = [
        {"role": "system",
         "content": "You are a terse weather summary generator. Always produce only the requested summary text."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=200,   # <-- FIXED (Groq uses max_tokens)
    )

    return response.choices[0].message.content.strip()


def weather_state_key(weather_json: dict) -> str:
    """Compute a small fingerprint of current weather to detect changes."""
    # Use current_weather fields and precipitation/humidity if present
    curr = weather_json.get("current_weather", {})
    key_parts = [
        str(curr.get("temperature")),
        str(curr.get("windspeed")),
        str(curr.get("winddirection")),
        str(curr.get("time")),
    ]
    # last hourly precipitation/humidity
    hourly = weather_json.get("hourly", {})
    if "time" in hourly and len(hourly["time"]) > 0:
        idx = len(hourly["time"]) - 1
        key_parts.append(str(hourly.get("precipitation", [None])[idx]))
        key_parts.append(str(hourly.get("relativehumidity_2m", [None])[idx]))
    return "|".join(key_parts)


def run(location: str = None, lat: float = None, lon: float = None, model: str = "llama-3.3-70b-versatile"):
    """
    Main runner. Provide either a place name in `location` OR numeric lat & lon.
    This loop polls Open-Meteo and prints a new summary when the weather fingerprint changes.
    """
    if location and (lat is not None or lon is not None):
        raise ValueError("Provide either location name or lat/lon, not both.")
    if location:
        geo = geocode_place(location)
        if not geo:
            raise RuntimeError(f"Could not geocode location: {location}")
        lat, lon, display_name = geo
    elif lat is not None and lon is not None:
        display_name = f"{lat:.5f},{lon:.5f}"
    else:
        raise ValueError("Either `location` or `lat` and `lon` must be provided.")

    print(f"Monitoring weather for: {display_name} (lat={lat}, lon={lon})")
    last_key = None

    try:
        while True:
            try:
                w = fetch_current_weather(lat, lon)
            except Exception as e:
                print(f"Error fetching weather: {e}")
                time.sleep(POLL_INTERVAL)
                continue

            key = weather_state_key(w)
            if key != last_key:
                prompt = brief_weather_prompt(display_name, w)
                # Get summary from Groq
                try:
                    summary = ask_groq_for_summary(prompt, model=model)
                except Exception as e:
                    print(f"Error calling Groq: {e}")
                    summary = "(error generating summary)"
                # Print only the summary (as requested)
                print(summary)
                # update last_key
                last_key = key
            # else: no change, nothing to print
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped by user.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Weather Summariser (Open-Meteo + Groq Llama)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--place", type=str, help="Place name to monitor (e.g. 'Bengaluru, India')")
    group.add_argument("--coords", type=str, help="Coordinates as lat,lon (e.g. '12.9716,77.5946')")
    parser.add_argument("--poll", type=int, default=POLL_INTERVAL, help="Polling interval in seconds")
    parser.add_argument("--model", type=str, default="llama-3.3-70b-versatile", help="Groq model name")
    args = parser.parse_args()

    POLL_INTERVAL = args.poll

    if args.place:
        run(location=args.place, model=args.model)
    else:
        lat_s, lon_s = args.coords.split(",")
        run(lat=float(lat_s.strip()), lon=float(lon_s.strip()), model=args.model)

