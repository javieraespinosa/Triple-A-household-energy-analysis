import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go

import numpy as np
import pandas as pd
import json
import re



def MDfy(obj):
    rex = r'^\s+'   # Match leading spaces
    return {k: re.sub(rex, '', v, flags=re.M) for (k, v) in obj.items()}

MD_TEXTS = MDfy({

    'header': '''
        # **Triple-A Demo**
        ## House 3394
    ''',

    'list-p1':'''
        * **Location**: Picardie
        * **Orientation**: South-east
        * **Occupants**: 1 retired lady
    ''',

    'list-p2':'''
        * **Typologie**: Worker house, 1926
        * **Masonry**: Red bricks
        * **Living space**: 85m²
    ''',

    'list-p3':'''
        * **Heating presets**: 20° day / 17° night
        * **Heating**: Gas
        * **Hot water**: Gas
    ''',

})



app = dash.Dash(__name__)
app.title = "Triple-A Demo"

def index_timestamp(df):
    df.index = pd.to_datetime(df['Timestamp'], unit='s')
    return df.drop(columns=['Timestamp'])


def group_hour_day(df, att):
    df = df[np.abs(df[att]-df[att].mean()) <= (3*df[att].std())]
    df = df.resample('H').sum()
    df = df.groupby([df.index.year, df.index.month, df.index.day, df.index.hour]).sum()
    df.index = df.index.set_names(['Year', 'Month', 'Day', 'Hour'])
    data={}
    for idx, df_select in df.groupby(level=[0, 1, 2]):
        per_hour = [0]*24
        for hour, val in df_select.loc[idx, att].iteritems():
            per_hour[hour] = val
        key = '{}-{}-{}'.format(idx[0], idx[1], idx[2])
        data[key] = per_hour
    return pd.DataFrame(data)





# Load data
indoor  = pd.read_csv("data/indoor-cleaned.csv")
outdoor = pd.read_csv("data/outdoor-cleaned.csv")
energy  = pd.read_csv("data/electricity-cleaned.csv")

# Timestamps as index
indoor  = index_timestamp(indoor).resample('1H').mean()
outdoor = index_timestamp(outdoor).resample('1H').mean()
energy  = index_timestamp(energy).resample('1H').sum()  # Aggregated sum 10 mins

# Heatmap 1
df = group_hour_day(energy, 'Electricity')
z  = []
for index, row in df.iterrows():
    z.append(row.values)



app.layout = html.Div(className='row', children=[

    dcc.Markdown(MD_TEXTS['header']),

    html.Div(className='row', children=[
        dcc.Markdown(MD_TEXTS['list-p1'], className='four columns'),
        dcc.Markdown(MD_TEXTS['list-p2'], className='four columns'),
        dcc.Markdown(MD_TEXTS['list-p3'], className='four columns'),
    ]),


    # --------------------------------
    # Electricity Graphs
    # --------------------------------

    html.Div(className='row', children=[

        dcc.Graph(className='six columns',
            id='electricity',
            figure=go.Figure(
                data=[
                    go.Scatter(name='Electricity',  x=energy.index,  y=energy['Electricity']),
                ],
                layout=go.Layout(
                    yaxis={"title": "Electricity (kWh)"},
                )
            )
        ),

        dcc.Graph(className='six columns',
            id='heatmap',
            figure=go.Figure(
                data=[
                    go.Heatmap(z=z, x=df.columns, y=df.index, colorbar={"title": "kWh"})
                ],
                layout=go.Layout(
                    yaxis={"title": "Day Hour"},
                ),
            )
        ),

    ]),


    # --------------------------------
    # Slider
    # --------------------------------
    html.Div(className='row', children=[
        dcc.RangeSlider(
            id='slider',
            min=0,
            max=len(energy.index.values),
            step=1,
            value=[0, len(energy.index.values)],
            marks={
                0: 'Dec 31, 2018',
                len(energy.index.values): 'Feb 27, 2019'
            },
            pushable=True,
        ),

    ]),




    # --------------------------------
    # Temperature and Humidity Graphs
    # --------------------------------

    html.Div(className='row', children=[

        dcc.Graph(className='six columns',
            id='temperature',
            figure=go.Figure(
                data=[
                    go.Scatter(name='Indoor',  x=indoor.index,  y=indoor['Temperature']),
                    go.Scatter(name='Outdoor', x=outdoor.index, y=outdoor['Temperature']),
                ],
                layout=go.Layout(
                    yaxis={"title": "Temperature °C"},
                )
            )
        ),

        dcc.Graph(className='six columns',
            id='humidity',
            figure=go.Figure(
                data=[
                    go.Scatter(name='Indoor',  x=indoor.index,  y=indoor['Humidity']),
                    go.Scatter(name='Outdoor', x=outdoor.index, y=outdoor['Humidity']),
                ],
                layout=go.Layout(
                    yaxis={"title": "Relative Humidity %"},
                )
            )
        ),

    ]),

    html.Div(id='output'),


])



# --------------------------------
# Callbacks
# --------------------------------

def update_xaxis(figure, ts1, ts2):
    figure['layout']['xaxis'] = {
        'range': [
            pd.Timestamp(ts1),
            pd.Timestamp(ts2)
        ],
        'rangeslider': {'visible': True},
        'type': 'date',
    }
    return figure



@app.callback(
    Output('humidity', 'figure'),
    [Input('slider', 'value')],
    [State('humidity', 'figure')]
)
def update_humidity(slider_values, figure):
    return update_xaxis(
        figure,
        indoor.index.values[slider_values[0]],
        indoor.index.values[slider_values[1]-1]
    )



@app.callback(
    Output('temperature', 'figure'),
    [Input('slider', 'value')],
    [State('temperature', 'figure')]
)
def update_temperature(slider_values, figure):
    return update_xaxis(
        figure,
        indoor.index.values[slider_values[0]],
        indoor.index.values[slider_values[1]-1]
    )



@app.callback(
    Output('electricity', 'figure'),
    [Input('slider', 'value')],
    [State('electricity', 'figure')]
)
def update_electricity(slider_values, figure):
    return update_xaxis(
        figure,
        energy.index.values[slider_values[0]],
        energy.index.values[slider_values[1]-1]
    )



@app.callback(
    Output('heatmap', 'figure'),
    [Input('slider', 'value')],
    [State('heatmap', 'figure')]
)
def update_heatmap(slider_values, figure):

    ts1=int(slider_values[0]/24)
    ts2=int((slider_values[1]-1)/24)
    return update_xaxis(
        figure,
        df.T.index.values[ts1],
        df.T.index.values[ts2]
    )


# --------------------------------
# Main
# --------------------------------
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)
