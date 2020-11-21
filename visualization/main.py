import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from visualization.data_retriever import *
from data.config import *


def create_geomap(filter_df, zoom=10,center={"lat": 40.7, "lon": -73.99}):
    fig = px.choropleth_mapbox(filter_df,
                               geojson=geo_json,
                               color="num_pickup",
                               locations="zone_name",
                               featureidkey="properties.zone",
                               mapbox_style="carto-positron",
                               hover_data=['zone_name','neighborhood','population','median_household_income','zipcode'],
                               zoom=zoom,
                               center=center,
                               opacity=0.5,
                               width=700, height=600
                               )
    return fig

df_original = get_merge_data()
geo_json = get_taxi_zone_geo()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(className='app-layout', children=[

    # Time control panel
    html.Div(className="row", id='control-panel-1',style={'width':'100%', 'columnCount': 4},children=[
        # html.Div(className="time selection", children=[
        #     dcc.Loading(
        #         className="loader",
        #         id="loading",
        #         type="default",
        #         children=[
        #             dcc.Markdown(id='data_summary_filtered', children='Selected {:,} trips'.format(len(df_original))),
        #             html.Progress(id="selected_progress", max=f"{len(df_original)}", value=f"{len(df_original)}"),
        #         ]),
        # ]),

        html.Div(className="time selection", children=[
            html.Label('Select Year'),
            dcc.RangeSlider(id='year',
                            value=[2019, 2020],
                            min=2019, max=2020,
                            marks={i: str(i) for i in range(2019, 2021)}),
        ]),
        html.Div(className="time selection", children=[
            html.Label('Select Month'),
            dcc.RangeSlider(id='months',
                            value=[3, 5],
                            min=3, max=5,
                            marks={i: str(i) for i in range(3, 6)}),
        ]),

        html.Div(className="time selection", children=[
            html.Label('Select Day'),
            dcc.RangeSlider(id='days',
                            value=[1, 31],
                            min=1, max=31,
                            marks={i: str(i) for i in range(1, 32, 5)}),
        ]),
        html.Div(className="time selection", children=[
            html.Label('Select Hours'),
            dcc.RangeSlider(id='hours',
                            value=[0, 23],
                            min=0, max=23,
                            marks={i: str(i) for i in range(0, 24, 3)}),
        ]),

    ]),
    html.Div(className="row", id='control-panel-2',children=[


        html.Div(className="time selection", children=[
            html.Label('Select a day of week'),
            dcc.Dropdown(id='weekday_name',
                         placeholder='Select a day of week',
                         options=[{'label': weekday_name, 'value': weekday_name} for weekday_name in weekday_names],
                         value=[],
                         multi=True),
        ])
    ]),
    html.Div(className="row", children=[
        dcc.Graph(id='map_id',
                  figure=create_geomap(df_original.loc['2020-5-12 18:00:00']))
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=5000)