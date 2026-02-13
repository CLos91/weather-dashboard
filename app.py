# CS361 Weather Dashboard - Main Program
# Carlos Ocampo

import os
import time
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# API key for OpenWeatherMap (free tier)
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(location):
    """Calls OpenWeatherMap and returns current weather for a given location."""

    # Clean up what the user typed
    cleaned = location.strip()

    # If they entered a zip code, tack on ,US so we don't get random countries
    if cleaned.isdigit() and len(cleaned) == 5:
        cleaned = cleaned + ",US"
    else:
        # The API doesn't recognize state abbreviations like ", CA"
        # so we strip those out and just append ,US
        import re
        cleaned = re.sub(r',\s*[A-Z]{2}$', '', cleaned)
        if ',US' not in cleaned.upper():
            cleaned = cleaned + ",US"

    params = {
        "q": cleaned,
        "appid": API_KEY,
        "units": "imperial"  # pulling in Fahrenheit so we don't lose precision converting
    }

    # Track how long the API takes to respond
    start_time = time.time()

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            weather = {
                "city": data["name"],
                "country": data["sys"].get("country", ""),
                "temp_f": round(data["main"]["temp"], 1),
                "temp_c": round((data["main"]["temp"] - 32) * 5 / 9, 1),
                "feels_like_f": round(data["main"]["feels_like"], 1),
                "feels_like_c": round((data["main"]["feels_like"] - 32) * 5 / 9, 1),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "wind_speed": round(data["wind"]["speed"], 1),
                "pressure": data["main"]["pressure"],
                "response_time_ms": round(elapsed * 1000),
                "success": True
            }
            return weather

        elif response.status_code == 404:
            return {
                "success": False,
                "error": f'Location "{location}" not found. Try a different city name or zip code.',
            }
        else:
            return {
                "success": False,
                "error": "Unable to fetch weather data. Please try again.",
            }

    except Exception:
        return {
            "success": False,
            "error": "Something went wrong. Please try again.",
        }


@app.route("/")
def index():
    """Serves the main page."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """Handles the search form, gets location from the user and returns weather JSON."""
    location = request.form.get("location", "").strip()

    if not location:
        return jsonify({
            "success": False,
            "error": "Please enter a location.",
            "suggestion": "Type a city name (e.g., 'Portland, OR') or zip code (e.g., '97201')"
        })

    weather = fetch_weather(location)
    return jsonify(weather)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  CS361 Weather Dashboard")
    print("  http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)