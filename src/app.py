import numpy as np
import pandas as pd

#import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats

from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime
import dash



df = pd.read_csv('../ikke_ep.csv')
#fil = askopenfilename()
#df = pd.read_csv(fil)
# "C:\Users\vetle\OneDrive\data_science\env\H39_15_juni_23.csv"

df = df.drop(columns = ['sleep_status','status','patient_id'])
df.time = pd.to_datetime(df.time)
df = df.sort_values(by = 'time' )
df['dato'] = df.time.dt.date
df.dato = pd.to_datetime(df.dato)
df['epilsepsi'] = False

#categories
categories = []
cats = df.columns[df.columns.str.contains('min')]
for i in cats:
    categories.append(i.replace('_min',''))

# Assuming your dfframe is named 'df'
# Select all columns except 'time' column
columns_to_diff = df.columns[1:]

# Calculate the difference for each column
diff_df = df[columns_to_diff].diff()
diff_df['time'] = df.time
diff_df['dato'] = df.dato
diff_df['epilsepsi'] = df.epilsepsi


app = dash.Dash(__name__)
server = app.server

def funk(df):

    diff_df = df.copy()
    
    # Define your list of strings
    dates = diff_df['dato'].dt.strftime("%U-%Y")
    dates = dates.unique()

    # To reduce the number of marks, let's space them out evenly
    step = max(1, len(dates) // 10)  # Show 10 evenly spaced marks at most
    marks = {i: dates[i] for i in range(0, len(dates), step)}

    app.layout = html.Div([
    dcc.Store(id='camera-data', storage_type='session'),
    dcc.Graph(
        id='3d-graph',
        style={'height': '80vh'}  # This sets the height to 80% of the viewport height
    ),
    html.Div([
        dcc.RangeSlider(
            id='range-slider',
            min=0,
            max=len(dates) - 1,
            value=[0, len(dates) - 1],
            marks=marks,
        )
    ], style={'margin-top': '30px'})  # Add 30 pixels of space above the slider
])

    @app.callback(
        Output('camera-data', 'data'),
        Input('3d-graph', 'relayoutData'),
        prevent_initial_call=True
    )
    def store_camera_data(relayoutData):
        if relayoutData is None:
            raise dash.exceptions.PreventUpdate
        if 'scene.camera' in relayoutData:
            return relayoutData['scene.camera']
        else:
            raise dash.exceptions.PreventUpdate

    @app.callback(
        Output('3d-graph', 'figure'),
        [Input('range-slider', 'value'),
        Input('camera-data', 'data')],
        prevent_initial_call=True
    )
    def update_graph(value, camera_data):
        min_val, max_val = map(int, value)
        min_date = datetime.strptime(dates[min_val] + "-Mon", '%U-%Y-%a')
        max_date = datetime.strptime(dates[max_val] + "-Mon", '%U-%Y-%a')
        mask = (diff_df.dato >= min_date) & (diff_df.dato <= max_date)
        subset_df = df.loc[mask]

        # Set the camera to the stored data, if it exists
        layout = go.Layout(
            scene=dict(
                xaxis=dict(title='HRV Max'),
                yaxis=dict(title='Relative Stroke Volume Max'),
                zaxis=dict(title='Respiration Rate Max'),
                camera=camera_data if camera_data is not None else dict()
            ),
            margin=dict(l=0, r=0, b=0, t=0)
        )

        return {
            'data': [go.Scatter3d(
                x=subset_df['heart_rate_variability_max'],
                y=subset_df['relative_stroke_volume_max'],
                z=subset_df['respiration_rate_max'],
                mode='markers',
                text='HRV Max: ' + subset_df['heart_rate_variability_max'].map(str) + ', ' +
                    'Relative Stroke Volume Max: ' + subset_df['relative_stroke_volume_max'].map(str) + ', ' +
                    'Respiration Rate Max: ' + subset_df['respiration_rate_max'].map(str) + ', ' +
                    'Heart Rate: ' + subset_df['heart_rate_max'].map(str),
                hoverinfo='text',
                hoverlabel=dict(
                    font_size=16
                ),
                marker=dict(
                    size=12,
                    color=subset_df['heart_rate_max'],
                    colorscale='Portland',
                    opacity=0.8,
                    colorbar=dict(
                        title="Heart Rate Max",
                        titleside='right',
                        titlefont=dict(
                            size=14,
                            family="Arial, sans-serif"
                        ),
                        tickmode="auto",
                        nticks=6,
                    )
                )
            )],
            'layout': layout
        }

    if __name__ == '__main__':
        app.run_server(debug=True)


funk(df)