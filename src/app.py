import numpy as np
import pandas as pd
import plotly.graph_objects as go
import base64
import io

from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from datetime import datetime

# Define common styles
FONT_FAMILY = (
    "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, "
    "Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif"
)

# Define slider container styles (currently not used directly, but available for future use)
slider_container_styles = {
    'padding': '20px 25px 10px 25px',
    'background': 'white',
    'borderRadius': '10px',
    'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    'margin': '10px auto',
    'width': '80%',
    'position': 'relative',
    'top': '-20px'
}

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    # Top section with title and date picker
    html.Div([
        # Empty div for left spacing
        html.Div(style={'flex': '1'}),
        
        # Centered title
        html.H1(
            "3D Visualisering",
            style={
                'textAlign': 'center',
                'margin': '20px',
                'fontFamily': FONT_FAMILY,
                'fontWeight': '600',
                'color': '#1a1a1a',
                'fontSize': '2.5rem',
                'flex': '1'
            }
        ),
        
        # Date filter on the right
        html.Div([
            html.P(
                "",
                style={
                    'margin': '0 0 15px 0',
                    'fontFamily': FONT_FAMILY,
                    'fontSize': '0.9rem',
                    'color': '#666',
                    'textAlign': 'left'
                }
            ),
            dcc.DatePickerRange(
                id='date-picker-range',
                style={
                    'margin': '0',
                    'display': 'block'
                },
                clearable=False,  # Prevent clearing the dates
                display_format='DD/MM/YYYY',  # Optional: customize date display format
                start_date_placeholder_text='Start Date',
                end_date_placeholder_text='End Date',
                updatemode='bothdates'
            )
        ], style={
            'flex': '1',
            'textAlign': 'right',
            'marginRight': '20px',
            'marginTop': '20px',
            'display': 'flex',
            'flexDirection': 'column'
        }),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'width': '100%'
    }),
    
    # Upload section
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a CSV File', style={'color': '#2563eb', 'textDecoration': 'underline'})
        ]),
        style={
            'width': '99%',
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
    
    html.Div(id='error-container'),
    dcc.Store(id='camera-store'),
    dcc.Store(id='stored-data'),
    dcc.Store(id='date-range-store'),
    
    # Graph and slider section
    html.Div([
        dcc.Graph(
            id='3d-graph',
            style={'height': '70vh'}
        ),
        
        html.Div(
            id='slider-container',
            style={
                'width': '80%',
                'margin': '40px auto',  # Increased margin
                'padding': '40px 25px 20px 25px',  # Increased top padding
                'fontFamily': FONT_FAMILY,
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
            }
        )
    ])
])


def parse_contents(contents):
    """Parse the uploaded CSV file."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df['time'] = pd.to_datetime(df['time'])
        return df
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise


@app.callback(
    [Output('stored-data', 'data'),
     Output('slider-container', 'children'),
     Output('error-container', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def process_data(contents, filename):
    if contents is None:
        return {}, None, ""
    
    try:
        # Parse the uploaded file
        df = parse_contents(contents)
        
        # Get unique dates and sort them
        dates = df['time'].dt.date.unique()
        dates.sort()
        
        # Prepare stored data (JSON-serializable)
        stored_data = {
            'df': df.to_dict('records'),
            'dates': [d.strftime('%d-%m-%Y') for d in dates]
        }
        
        # Create slider component
        slider_component = html.Div([
            dcc.RangeSlider(
                id='date-slider',
                min=0,
                max=len(dates) - 1,
                value=[0, len(dates) - 1],
                marks={
                    i: {
                        'label': dates[i].strftime('%d-%m-%Y'),
                        'style': {
                            'white-space': 'nowrap',
                            'padding-top': '10px',
                            'font-size': '11px'
                        }
                    }
                    for i in range(0, len(dates), max(1, len(dates) // 8))
                },
                step=1,
                tooltip={
                    "placement": "bottom",
                    "always_visible": True
                },
                allowCross=False
            )
        ])
        
        return stored_data, slider_component, ""
    
    except Exception as e:
        error_message = f"Error processing file: {str(e)}"
        return {}, None, error_message


# Callback to store camera position from 3D graph interactions
@app.callback(
    Output('camera-store', 'data'),
    Input('3d-graph', 'relayoutData'),
    prevent_initial_call=True
)
def store_camera(relayout_data):
    if relayout_data and 'scene.camera' in relayout_data:
        return relayout_data['scene.camera']
    raise PreventUpdate


# Callback to update the 3D graph based on stored data and slider selection
@app.callback(
    Output('3d-graph', 'figure'),
    [Input('stored-data', 'data'),
     Input('date-slider', 'value')],
    State('camera-store', 'data'),
    prevent_initial_call=True
)
def update_graph(stored_data, slider_value, camera_pos):
    if not stored_data:
        raise PreventUpdate
    
    try:
        # Reconstruct DataFrame from stored data
        df = pd.DataFrame(stored_data['df'])
        df['time'] = pd.to_datetime(df['time'])
        
        # Convert stored string dates back to datetime
        dates = pd.to_datetime(stored_data['dates'])
        
        # Filter data based on slider values if available
        if slider_value is not None:
            min_date = dates[slider_value[0]]
            max_date = dates[slider_value[1]]
            df = df[(df['time'].dt.date >= min_date.date()) &
                    (df['time'].dt.date <= max_date.date())]
        
        # Create the 3D scatter plot figure
        figure = {
            'data': [
                go.Scatter3d(
                    x=df['heart_rate_variability_max'],
                    y=df['heart_rate_max'],
                    z=df['respiration_rate_max'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=df['relative_stroke_volume_max'],
                        colorscale='Viridis',
                        opacity=0.8,
                        colorbar=dict(
                            title=dict(
                                text="Relative Stroke Volume",
                                side="right",  # Use 'side' within the title dictionary
                                font=dict(
                                    family=FONT_FAMILY,
                                    size=14
                                )
                            ),
                            tickfont=dict(
                                family=FONT_FAMILY
                            )
                        )
                    ),
                    hovertemplate=(
                        '<b>Time</b>: %{customdata}<br>' +
                        '<b>HRV Max</b>: %{x:.1f}<br>' +
                        '<b>HR Max</b>: %{y:.1f}<br>' +
                        '<b>RR Max</b>: %{z:.1f}<br>' +
                        '<b>RSV Max</b>: %{marker.color:.1f}<br>'
                    ),
                    customdata=df['time'].dt.strftime('%Y-%m-%d %H:%M')
                )
            ],
            'layout': go.Layout(
                scene=dict(
                    xaxis=dict(
                        title=dict(
                            text='HRV Max',
                            font=dict(
                                family=FONT_FAMILY,
                                size=14
                            )
                        )
                    ),
                    yaxis=dict(
                        title=dict(
                            text='Heart Rate Max',
                            font=dict(
                                family=FONT_FAMILY,
                                size=14
                            )
                        )
                    ),
                    zaxis=dict(
                        title=dict(
                            text='Respiration Rate Max',
                            font=dict(
                                family=FONT_FAMILY,
                                size=14
                            )
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
        }
        
        return figure
    
    except Exception as e:
        print(f"Error in update_graph: {str(e)}")
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

# Replace the two callbacks with a single one
@app.callback(
    [Output('date-slider', 'value'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('date-slider', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')],
    [State('stored-data', 'data')],
    prevent_initial_call=True
)
def sync_date_controls(slider_value, picker_start, picker_end, stored_data):
    if not stored_data:
        raise PreventUpdate
        
    dates = pd.to_datetime(stored_data['dates'])
    ctx = callback_context
    
    if not ctx.triggered:
        raise PreventUpdate
        
    trigger_id = ctx.triggered[0]['prop_id']
    
    if 'date-slider' in trigger_id:
        # Slider was moved
        start_date = dates[slider_value[0]]
        end_date = dates[slider_value[1]]
        return slider_value, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    else:
        # Date picker was changed
        if not all([picker_start, picker_end]):
            raise PreventUpdate
        start_idx = dates.get_loc(pd.to_datetime(picker_start).strftime('%Y-%m-%d'))
        end_idx = dates.get_loc(pd.to_datetime(picker_end).strftime('%Y-%m-%d'))
        return [start_idx, end_idx], picker_start, picker_end

if __name__ == '__main__':
    app.run_server(debug=True)
