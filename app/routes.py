import sys
import os
import json
from app import app
from flask import render_template, request
from datetime import datetime, timedelta
from app.utils.weather_api import get_yearly_weather_data_for_day, get_lat_lng
from app.utils.charting import create_weather_chart
from config import config
from typing import Tuple

def get_default_values():
    today = datetime.now()
    previous_day = today - timedelta(days=1)
    return {
        'start_year': 2000,
        'end_year': today.year,
        'month': previous_day.strftime('%m'),
        'day': previous_day.strftime('%d'),
        'units': 'imperial'
    }

def format_date(month: str, day: str) -> Tuple[str, str]:
    month_name = datetime.strptime(month, '%m').strftime('%B')
    day_num = int(day)
    day_suffix = 'th' if 4 <= day_num <= 20 or 24 <= day_num <= 30 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day_num % 10, 'th')
    day_formatted = f"{day_num}{day_suffix}"
    return month_name, day_formatted

def generate_temperature_charts(df, month_name, day_formatted, location_selection, units):
    temperature_metrics = [
        (['temperature_morning', 'temperature_afternoon'], 'Temperature in Morning and Afternoon'),
        (['temperature_evening', 'temperature_night'], 'Temperature in Evening and Night'),
        (['temperature_min', 'temperature_max'], 'Min and Max Temperature')
    ]
    colors = ['#87ceeb', '#4682b4']
    charts = []

    for metric_columns, title in temperature_metrics:
        chart_html = create_weather_chart(
            df, month_name, day_formatted, location_selection,
            metric_columns=metric_columns,
            colors=colors,
            is_temperature=True,
            units=units
        )
        charts.append(chart_html)

    return charts

def generate_metric_charts(df, month_name, day_formatted, location_selection, metrics, units):
    charts_html = {}
    for item in metrics:
        chart_html = create_weather_chart(
            df, month_name, day_formatted, location_selection,
            metric_columns=[item['metric']],
            metric_label=item['label'],
            colors=[item['color']],
            is_temperature=False,
            units=units
        )
        charts_html[item['metric']] = chart_html
    return charts_html

def handle_error(e):
    error_message = "An unexpected error occurred: " + str(e)
    return render_template('error.html', error_message=error_message)

@app.route('/', methods=['GET', 'POST'])
def index():
    defaults = get_default_values()
    
    if request.method == 'POST':
        try:
            day = request.form.get('day', defaults['day'])
            month = request.form.get('month', defaults['month'])
            start_year = request.form.get('start_year', defaults['start_year'])
            end_year = request.form.get('end_year', defaults['end_year'])
            units = request.form.get('unit_system', defaults['units'])
            temperature_unit = '°F' if units == 'imperial' else '°C'

            if end_year < start_year:
                return render_template('error.html', error_message="The end year cannot be before the start year.")

            location_selection = request.form['location-input']
            lat, lon, country_code = get_lat_lng(location=location_selection, api_key=config.api_key_google_maps)

            cleaned_location = request.form.get('cleaned_location')
            if cleaned_location and not cleaned_location.startswith(','):
                location_selection = cleaned_location

            month_name, day_formatted = format_date(month, day)
            current_year = datetime.now().year
            selected_date = datetime(current_year, int(month), int(day))
            is_future_date = selected_date > datetime.now()

            location_str = (
                f"Here is how weather on <strong>{month_name}</strong> <strong>{day_formatted}</strong> in <strong>{location_selection}</strong> "
                f"has trended from <strong>{start_year}</strong> to <strong>{end_year}</strong>"
            )

            df = get_yearly_weather_data_for_day(month=month, day=day, country_code=country_code,
                                                 lat=lat, lon=lon,
                                                 start_year=start_year, end_year=end_year,
                                                 units=units, api_key=config.api_key_openweathermap)
            
            temperature_charts = generate_temperature_charts(df, month_name, day_formatted, location_selection, units)
            metrics = [
                {'metric': 'precipitation', 'label': 'Precipitation (mm)', 'color': '#ffc107'},
                {'metric': 'cloud_cover', 'label': 'Cloud Cover (%)', 'color': '#ff7043'},
                {'metric': 'humidity', 'label': 'Humidity (%)', 'color': '#8bc34a'},                
                {'metric': 'pressure', 'label': 'Atmospheric Pressure (hPa)', 'color': '#9b59b6'}
            ]
            other_charts_html = generate_metric_charts(df, month_name, day_formatted, location_selection, metrics, units)

            return render_template('results.html', 
                                   location_str=location_str,
                                   chart1=temperature_charts[0],
                                   chart2=temperature_charts[1],
                                   chart3=temperature_charts[2],
                                   other_charts_html=other_charts_html,
                                   is_future_date=is_future_date,
                                   lat=lat,
                                   lon=lon)
        
        except ValueError as ve:
            return render_template('error.html', error_message=str(ve))
        except Exception as e:
            return handle_error(e)

    return render_template('index.html',
                           start_year=defaults['start_year'],
                           end_year=defaults['end_year'],
                           month=defaults['month'],
                           day=defaults['day'])

if __name__ == '__main__':
    app.run(debug=True)
