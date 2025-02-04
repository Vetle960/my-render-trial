import numpy as np
import pandas as pd
import plotly.graph_objects as go
import base64
import io

from dash import Dash, dcc, html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from datetime import datetime

# Define common styles
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif"

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.H1("3D Data Visualization", 
            style={
                'textAlign': 'center', 
                'margin': '20px',
                'fontFamily': FONT_FAMILY,
                'fontWeight': '600',
                'color': '#1a1a1a',
                'fontSize': '2.5rem'
            }),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a CSV File', style={'color': '#2563eb', 'textDecoration': 'underline'})
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '8px',
            'textAlign': 'center',
            'margin': '10px',
            'fontFamily': FONT_FAMILY,
            'color': '#4b5563',
            'backgroundColor': '#f9fafb',
            'transition': 'border-color 0.3s ease',
            'cursor': 'pointer'
        },
        multiple=False
    ),
    
    html.Div(id='error-container', 
             style={
                 'color': '#dc2626',
                 'margin': '10px',
                 'textAlign': 'center',
                 'fontFamily': FONT_FAMILY,
                 'fontSize': '0.875rem'
             }),
    
    # Add camera store
    dcc.Store(id='camera-store', storage_type='memory'),
    
    # Store for the data
    dcc.Store(id='stored-data'),
    
    dcc.Graph(
        id='3d-graph',
        style={'height': '70vh'}  # Slightly reduced height to make room for slider
    ),
    
    # Slider container with styling
    html.Div([
        html.P("Time Range Filter", 
               style={
                   'textAlign': 'center',
                   'margin': '10px',
                   'fontFamily': FONT_FAMILY,
                   'fontWeight': '500',
                   'color': '#1a1a1a',
                   'fontSize': '1.125rem'
               }),
        html.Div(id='slider-container',
                 style={
                     'width': '80%',
                     'margin': 'auto',
                     'padding': '20px',
                     'fontFamily': FONT_FAMILY
                 })
    ])
])

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = df.drop(columns=['sleep_status', 'status', 'patient_id'], errors='ignore')
        df['time'] = pd.to_datetime(df.time)
        return df
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

@app.callback(
    [Output('stored-data', 'data'),
     Output('slider-container', 'children'),
     Output('error-container', 'children')],
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def process_data(contents):
    if contents is None:
        raise PreventUpdate
    
    try:
        df = parse_contents(contents)
        
        # Create dates for slider
        dates = df['time'].dt.date.unique()
        dates.sort()
        
        # Create marks for slider
        num_marks = min(10, len(dates))  # Maximum 10 marks
        step = max(1, len(dates) // num_marks)
        marks = {i: dates[i].strftime('%Y-%m-%d') 
                for i in range(0, len(dates), step)}
        
        slider = dcc.RangeSlider(
            id='time-slider',
            min=0,
            max=len(dates) - 1,
            value=[0, len(dates) - 1],
            marks=marks,
            step=1,
            tooltip={"placement": "bottom", "always_visible": True}
        )
        
        # Store data
        stored_data = {
            'df': df.to_dict('records'),
            'dates': [d.strftime('%Y-%m-%d') for d in dates]
        }
        
        return stored_data, slider, ""
    
    except Exception as e:
        return None, None, f"Error processing file: {str(e)}"

# Add callback to store camera position
@app.callback(
    Output('camera-store', 'data'),
    Input('3d-graph', 'relayoutData'),
    prevent_initial_call=True
)
def store_camera(relayout_data):
    if relayout_data and 'scene.camera' in relayout_data:
        return relayout_data['scene.camera']
    raise PreventUpdate

@app.callback(
    Output('3d-graph', 'figure'),
    [Input('stored-data', 'data'),
     Input('time-slider', 'value')],
    [State('camera-store', 'data')],  # Add camera state
    prevent_initial_call=True
)
def update_graph(stored_data, slider_value, camera_pos):
    if not stored_data:
        raise PreventUpdate
    
    try:
        # Reconstruct DataFrame
        df = pd.DataFrame(stored_data['df'])
        df['time'] = pd.to_datetime(df['time'])
        dates = stored_data['dates']
        
        # Filter by slider if available
        if slider_value is not None:
            min_date = pd.to_datetime(dates[slider_value[0]])
            max_date = pd.to_datetime(dates[slider_value[1]])
            df = df[(df['time'].dt.date >= min_date.date()) &  
                   (df['time'].dt.date <= max_date.date())]
        
        layout = go.Layout(
            scene=dict(
                xaxis=dict(
                    title='HRV Max',
                    titlefont=dict(
                        family=FONT_FAMILY,
                        size=14
                    )
                ),
                yaxis=dict(
                    title='Relative Stroke Volume Max',
                    titlefont=dict(
                        family=FONT_FAMILY,
                        size=14
                    )
                ),
                zaxis=dict(
                    title='Respiration Rate Max',
                    titlefont=dict(
                        family=FONT_FAMILY,
                        size=14
                    )
                ),
                bgcolor='rgb(250,250,250)',
                camera=camera_pos if camera_pos else dict()
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            paper_bgcolor='white',
            uirevision=True,
            font=dict(
                family=FONT_FAMILY
            )
        )
        
        figure = {
            'data': [go.Scatter3d(
                x=df['heart_rate_variability_max'],
                y=df['relative_stroke_volume_max'],
                z=df['respiration_rate_max'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['heart_rate_max'],
                    colorscale='Portland',
                    opacity=0.8,
                    colorbar=dict(
                        title=dict(
                            text="Heart Rate",
                            font=dict(
                                family=FONT_FAMILY,
                                size=14
                            )
                        ),
                        titleside="right",
                        tickfont=dict(
                            family=FONT_FAMILY
                        )
                    )
                ),
                hovertemplate=
                '<b>Time</b>: %{customdata}<br>' +
                '<b>HRV Max</b>: %{x:.1f}<br>' +
                '<b>RSV Max</b>: %{y:.1f}<br>' +
                '<b>RR Max</b>: %{z:.1f}<br>' +
                '<b>HR Max</b>: %{marker.color:.1f}<br>',
                customdata=df['time'].dt.strftime('%Y-%m-%d %H:%M')
            )],
            'layout': layout
        }
        
        return figure
    
    except Exception as e:
        return {
            'data': [],
            'layout': go.Layout(
                scene=dict(
                    xaxis=dict(title='Error occurred'),
                    yaxis=dict(title=''),
                    zaxis=dict(title='')
                )
            )
        }

if __name__ == '__main__':
    app.run_server(debug=True) 