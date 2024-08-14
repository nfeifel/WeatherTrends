from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple
import requests
from config import apis

def get_weather_data(lat: float, lon: float, date: str, units: str, api_key: str) -> Dict[str, Any]:
    """Get weather data for a specific date and location."""
    try:
        weather_data_query = f"{apis['data']}onecall/day_summary"
        params = {
            'lat': lat,
            'lon': lon,
            'date': date,
            'units': units,
            'appid': api_key
        }
        response = requests.get(weather_data_query, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting weather data for {lat}, {lon} on {date}: {e}")
        raise

def extract_weather_data(weather_data_response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant weather data from the response."""
    return {
        "cloud_cover": weather_data_response['cloud_cover']['afternoon'],
        "humidity": weather_data_response['humidity']['afternoon'],
        "precipitation": weather_data_response['precipitation']['total'],
        "pressure": weather_data_response['pressure']['afternoon'],
        "temperature_min": weather_data_response['temperature']['min'],
        "temperature_max": weather_data_response['temperature']['max'],
        "temperature_morning": weather_data_response['temperature']['morning'],
        "temperature_afternoon": weather_data_response['temperature']['afternoon'],
        "temperature_evening": weather_data_response['temperature']['evening'],
        "temperature_night": weather_data_response['temperature']['night'],
    }

def get_yearly_weather_data_for_day(month: str, day: str, country_code: str, lat: float, lon: float, api_key: str, units: str = 'imperial', start_year: str = '2019', end_year: str = str(datetime.now().year)) -> pd.DataFrame:
    """Get yearly weather data for a specific day."""
    years = list(range(int(start_year), (int(end_year) + 1)))
    dates = [f"{year}-{month}-{day}" for year in years]

    weather_data_list = []

    for date in dates:
        try:
            weather_data_response = get_weather_data(lat, lon, date, units, api_key)
            weather_data = extract_weather_data(weather_data_response)
            weather_data.update({
                "country_code": country_code,
                "lat": lat,
                "lon": lon,
                "date": date,
                "year": date.split('-')[0],
                "month": month,
                "day": day,
                "units": units
            })
            weather_data_list.append(weather_data)
        except Exception as e:
            logging.error(f"Skipping date {date} due to error: {e}")

    return pd.DataFrame(weather_data_list)

def make_google_places_request(url: str, params: dict) -> dict:
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_country_code(place_id: str, api_key: str) -> str:
    place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    place_details_params = {
        'place_id': place_id,
        'fields': 'address_components',
        'key': api_key
    }
    place_details_data = make_google_places_request(place_details_url, place_details_params)
    
    for component in place_details_data['result'].get('address_components', []):
        if 'country' in component['types']:
            return component['short_name']

    return ''

def get_lat_lng(location: str, api_key: str) -> Tuple[float, float, str]:
    find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    find_place_params = {
        'input': location,
        'inputtype': 'textquery',
        'fields': 'geometry,place_id',
        'key': api_key
    }
    find_place_data = make_google_places_request(find_place_url, find_place_params)

    if not find_place_data['candidates']:
        raise ValueError("No location was selected. Please provide one and resubmit!")

    lat = find_place_data['candidates'][0]['geometry']['location']['lat']
    lng = find_place_data['candidates'][0]['geometry']['location']['lng']
    place_id = find_place_data['candidates'][0]['place_id']

    country_code = get_country_code(place_id, api_key)
    return lat, lng, country_code