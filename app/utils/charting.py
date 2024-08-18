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
            text=f'{label_names_string}',
            x=0.5, y=0.95,
            xanchor='center', yanchor='top',
            font=dict(size=17, weight='bold')
        ),
        xaxis_title='Year',
        yaxis_title=f'Temperature ({y_axis_unit})' if is_temperature else metric_label,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            fixedrange=True
        ),
        legend=dict(
            x=0.5, y=1.14,
            xanchor='center', yanchor='top',
            orientation='h',
            bordercolor='Grey',
            borderwidth=0.25,
            font=dict(size=11)
        ),
        autosize=True,
        height=None,  # Let the container control the height
        hoverlabel=dict(
            bgcolor="white",
            font_size=14
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',  # Enable tooltips
        dragmode=False,       # Disable panning and box select
        yaxis=dict(fixedrange=True),  # Disable zoom on y-axis
        annotations=[
            dict(
                text=f"{month} {day} | {location}",
                xref='paper', yref='paper',
                x=0.5, y=1.23,
                xanchor='center', yanchor='top',
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

    label_names_string = ' & '.join(label_names_list) + ' Temperature' if is_temperature else metric_label

    fig.update_layout(**create_layout(label_names_string, metric_label, is_temperature, tickvals, ticktext, month, day, location, units))

    # Enable tooltips and download option, disable other interactivity
    config = {
        'staticPlot': False,  # Allows interactivity (tooltips)
        'displayModeBar': True,  # Show the mode bar for downloading
        'scrollZoom': False,  # Disable zooming with scroll
        'displaylogo': False,  # Remove the Plotly logo
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 
                                   'zoomIn2d', 'zoomOut2d', 'autoScale2d', 
                                   'resetScale2d', 'hoverCompareCartesian', 
                                   'hoverClosestCartesian', 'toggleSpikelines']
    }

    return fig.to_html(full_html=False, include_plotlyjs='cdn', config=config)
