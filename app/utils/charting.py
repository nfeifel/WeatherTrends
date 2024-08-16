import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

def calculate_ticks(years: pd.Series, num_ticks: int = 10) -> Tuple[np.ndarray, List[str]]:
    """Calculate tick values and labels for the x-axis."""
    tickvals = np.linspace(min(years), max(years), num_ticks)
    ticktext = [str(int(val)) for val in tickvals]
    return tickvals, ticktext

def create_layout(label_names_string: str, metric_label: str, is_temperature: bool, tickvals: np.ndarray, ticktext: List[str], month: str, day: str, location: str, units: str) -> dict:
    """Create layout configuration for the Plotly chart."""
    # Determine the temperature unit  
    y_axis_unit = '°F' if units == 'imperial' else '°C'
    return dict(
        title=dict(
            text=f'{label_names_string} Over Time',
            x=0.5, y=0.99,
            xanchor='center', yanchor='top',
            font=dict(size=18, weight='bold')
        ),
        xaxis_title='Year',
        yaxis_title=f'Temperature ({y_axis_unit})' if is_temperature else metric_label,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext
        ),
        legend=dict(
            x=0.5, y=0.96,
            xanchor='center', yanchor='bottom',
            orientation='h',
            bordercolor='Grey',
            borderwidth=0.5,
            font=dict(size=12)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, t=50, b=50),
        # width=625,
        # height=300,
        annotations=[
            dict(
                text=f"<b>{month} {day} | {location}</b>",
                xref='paper', yref='paper',
                x=-0.08, y=-0.15,
                xanchor='left', yanchor='top',
                showarrow=False,
                font=dict(size=12, color='Grey')
            )
        ]
    )

def create_weather_chart(
    weather_data: pd.DataFrame, 
    month: str, 
    day: str, 
    location: str, 
    metric_columns: List[str],
    metric_label: str = 'Weather Metric', 
    colors: List[str] = ['blue'],    
    is_temperature: bool = False,
    units: str = 'imperial'
) -> str:
    """Create a Plotly chart for weather metrics and return the HTML string."""

    fig = go.Figure()
    years = pd.to_numeric(weather_data['year'])
    label_names_list = []

    for col, color in zip(metric_columns, colors):
        label_name = col.split('_')[-1].capitalize() if is_temperature else metric_label
        label_names_list.append(label_name)

        fig.add_trace(go.Scatter(
            x=years, 
            y=weather_data[col], 
            mode='lines+markers', 
            name=label_name,
            line=dict(shape='linear', color=color)
        ))

    tickvals, ticktext = calculate_ticks(years)

    label_names_string = ' and '.join(label_names_list) + ' Temperature' if is_temperature else metric_label

    fig.update_layout(**create_layout(label_names_string, metric_label, is_temperature, tickvals, ticktext, month, day, location, units))

    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'staticPlot': False, 'displayModeBar': False, 'scrollZoom': False})