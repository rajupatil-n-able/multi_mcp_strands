from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather MCP Server")

USER_AGENT = "strands-msp-weather/1.0"


def _fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _resolve_city(city: str) -> tuple[float, float, str, str]:
    encoded_city = quote(city)
    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={encoded_city}&count=1&language=en&format=json"
    )
    data = _fetch_json(url)
    results = data.get("results") or []
    if not results:
        raise ValueError(f"Could not find location for '{city}'.")

    location = results[0]
    return (
        location["latitude"],
        location["longitude"],
        location.get("name", city),
        location.get("country", "Unknown country"),
    )


def _format_weather_code(code: int) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, f"Weather code {code}")


@mcp.tool()
def current_weather(city: str) -> dict:
    """
    Return the current weather for a city using Open-Meteo.
    Example: city='Pune' or city='London'
    """
    try:
        latitude, longitude, resolved_name, country = _resolve_city(city)
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m"
            "&timezone=auto"
        )
        data = _fetch_json(url)
        current = data["current"]
        units = data.get("current_units", {})
        return {
            "location": f"{resolved_name}, {country}",
            "temperature": f"{current['temperature_2m']} {units.get('temperature_2m', '°C')}",
            "feels_like": f"{current['apparent_temperature']} {units.get('apparent_temperature', '°C')}",
            "humidity": f"{current['relative_humidity_2m']} {units.get('relative_humidity_2m', '%')}",
            "precipitation": f"{current['precipitation']} {units.get('precipitation', 'mm')}",
            "wind_speed": f"{current['wind_speed_10m']} {units.get('wind_speed_10m', 'km/h')}",
            "condition": _format_weather_code(current['weather_code']),
            "observed_at": current["time"],
        }
    except ValueError as exc:
        return {"error": str(exc)}
    except (HTTPError, URLError, TimeoutError) as exc:
        return {"error": f"Weather service unavailable: {exc}"}


@mcp.tool()
def weather_forecast(city: str, days: int = 3) -> dict:
    """
    Return a short daily forecast for a city.
    Days can be between 1 and 7.
    Example: city='Bengaluru', days=3
    """
    forecast_days = min(max(days, 1), 7)
    try:
        latitude, longitude, resolved_name, country = _resolve_city(city)
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&forecast_days={forecast_days}&timezone=auto"
        )
        data = _fetch_json(url)
        daily = data["daily"]
        units = data.get("daily_units", {})
        forecast = []
        for index, date_value in enumerate(daily["time"]):
            forecast.append(
                {
                    "date": date_value,
                    "condition": _format_weather_code(daily["weather_code"][index]),
                    "max_temp": f"{daily['temperature_2m_max'][index]} {units.get('temperature_2m_max', '°C')}",
                    "min_temp": f"{daily['temperature_2m_min'][index]} {units.get('temperature_2m_min', '°C')}",
                    "precipitation": f"{daily['precipitation_sum'][index]} {units.get('precipitation_sum', 'mm')}",
                }
            )
        return {
            "location": f"{resolved_name}, {country}",
            "forecast_days": forecast_days,
            "forecast": forecast,
        }
    except ValueError as exc:
        return {"error": str(exc)}
    except (HTTPError, URLError, TimeoutError) as exc:
        return {"error": f"Weather service unavailable: {exc}"}


@mcp.resource("info://server")
def server_info() -> str:
    """Static resource describing this MCP server."""
    return (
        "Weather MCP Server\n"
        "Tools: current_weather, weather_forecast\n"
        "Transport: stdio"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")



