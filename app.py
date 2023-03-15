import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, Input, Output, dash_table
from dash import html as html

app = Dash(__name__)
app.title = "NYC High School Demographics"

# data loading
schools = pd.read_csv('data/schools_final.csv')
zip_means = pd.read_csv('data/zip_means.csv')
district_means = pd.read_csv('data/district_means.csv')

# load for map
# zips
zip_geos = gpd.read_file('data/zip_geos.json')
zip_geos['geometry'] = zip_geos.to_crs(zip_geos.estimate_utm_crs()).simplify(10).to_crs(zip_geos.crs)
# school districts
district_geos = gpd.read_file('data/district_geos.json')
district_geos['geometry'] = district_geos.to_crs(district_geos.estimate_utm_crs()).simplify(10).to_crs(district_geos.crs)

#dictionaries for choosing between dfs
dict_geos = {'School Districts': district_geos, 'Zip Codes': zip_geos}
dict_means = {'School Districts': district_means, 'Zip Codes': zip_means}


def region_pick(region):
    if region == 'School Districts':
        region_col = 'school_dist'
    else:
        region_col = 'Zipcode'
    return region_col

# app
app.layout = html.Div([

    html.Div([
        html.H1('NYC High School Demographics'),
        html.P(
            children=[
                'by Rory Butler - roryb102@gmail.com - ',
                dcc.Link(
                    href='https://github.com/rb2661/NYC_Schools'
                )], style={'font-size': 12}),
        html.P('Select a demographic and year to update the map of NYC'),
        html.P('You have the option to view NYC by School Districts or Zip Codes'),
        html.P('Click on the map to see data specific to schools in that region'),
        dcc.Dropdown(
            id='regions',
            options=['School Districts', 'Zip Codes'],
            value=list(dict_geos.keys())[0]
            ),
        dcc.Dropdown(
            id='demographic',
            options=['Graduation Rate', 'Asian %', 'Hispanic %', 'Black %', 'Poverty %'],
            value='Graduation Rate'
            ),
        dcc.RadioItems(
                id='year',
                options=[2013, 2014, 2015, 2016, 2017],
                value=2017,
                inline=True
            )
    ], style={'width': '60%', 'display': 'inline-block', 'font-family': 'Helvetica'}),

    html.Div(
        dcc.Loading(id='loading-graph',
                    children=[html.Div([dcc.Graph(id='map')])],
                    type='default'
                    ),
        style={'width': '60%', 'display': 'inline-block', 'padding': '0 10'}),
    html.Div([
        html.H2('Selected School District or Zip Code:', style={'textAlign': 'center'}),
        html.H4(id='location_code', style={'textAlign': 'center'}),
        dcc.Graph(id='time-series'),
        html.P('The table lists the schools\' demographic data for the selected year only', style={'textAlign': 'center'}),
        html.H4(id='schools_table')
    ], style={'display': 'inline-block', 'float': 'right', 'width': '40%', 'font-family': 'Helvetica'}),

])


@app.callback(
    Output('map', 'figure'),
    Input('regions', 'value'),
    Input('demographic', 'value'),
    Input('year', 'value'))
def display_choropleth(regions, demographic, year):
    df = dict_means[regions]
    dff = df[df['Cohort Year'] == year]
    geojson = dict_geos[regions]

    locations = ''
    if regions == 'School Districts':
        locations = 'school_dist'
    else:
        locations = 'Zipcode'

    feature_id = ''
    if regions == 'School Districts':
        feature_id = 'properties.school_dist'
    else:
        feature_id = 'properties.ZIPCODE'

    fig = px.choropleth_mapbox(dff, geojson=geojson, color=demographic,
                               locations=locations, featureidkey=feature_id,
                               center={'lat': 40.7128, 'lon': -74.0060},
                               mapbox_style='carto-positron', zoom=9,
                               color_continuous_scale='haline')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0}, height=700)

    # add school points
    '''
    fig.add_scattermapbox(
        lat=schools.Latitude,
        lon=schools.Longitude,
        text=schools.school_name,
        marker_color='rgb(3, 127, 252)'
    )
    '''
    return fig


@app.callback(
    Output('location_code', 'children'),
    Input('map', 'clickData'))
def display_location_code(clickData):
    location_display = clickData['points'][0]['location']
    return location_display


@app.callback(
    Output('schools_table', 'children'),
    Input('map', 'clickData'),
    Input('regions', 'value'),
    Input('demographic', 'value'),
    Input('year', 'value'))
def display_school_table(clickData, regions, demographic, year):
    schools2 = schools[schools[region_pick(regions)] == clickData['points'][0]['location']]
    schools3 = schools2[schools2['Cohort Year'] == year]
    schools4 = schools3[['School Name', demographic]]
    columns = [{"name": i, "id": i, } for i in schools4.columns]
    df_data = schools4.to_dict('records')

    schooltable = dash_table.DataTable(
        data=df_data,
        columns=columns,
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_header={
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_cell={
            # all three widths are needed
            'minWidth': '75px', 'width': '75px', 'maxWidth': '180px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'left'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'School Name'},
             'width': '180px'}
            ],
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df_data
        ],
        tooltip_duration=None
    )

    return schooltable


@app.callback(
    Output('time-series', 'figure'),
    Input('map', 'clickData'),
    Input('regions', 'value'),
    Input('demographic', 'value'))
def time_series_plot(clickData, regions, demographic):
    schools2 = schools[schools[region_pick(regions)] == clickData['points'][0]['location']]
    schools3 = schools2[['School Name', 'Cohort Year', demographic]]
    schools4 = schools3.sort_values(by=['School Name', 'Cohort Year'], ascending=[True, True])

    fig = px.line(schools4, x='Cohort Year', y=demographic, color='School Name',
                  title='School Demographic by Year', markers=True)
    fig.update_layout(showlegend=False, title_x=0.5)
    fig.update_xaxes(nticks=5)
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left', text='')

    fig.update_layout(height=500, margin={'l': 10, 'b': 10, 'r': 10, 't': 40})

    return fig


app.run_server(debug=True)
