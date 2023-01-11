import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, Input, Output, dash_table
from dash import html as html

app = Dash(__name__)
app.title = "NYC High Schools"

# data loading
schools = pd.read_csv('data/schools_final.csv')
zip_means = pd.read_csv('data/zip_means.csv')
# load for map
zip_geos = gpd.read_file('data/zip_geos.json')

# app
app.layout = html.Div([

    html.Div([
        html.H1('NYC High School Demographics'),
        html.P('Select a demographic:'),
        dcc.Dropdown(
            id='demographic',
            options=['Graduation Rate', 'Asian %', 'Hispanic %', 'Black %', 'Poverty %'],
            value='Graduation Rate'
            )
    ], style={'width': '60%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='map')
    ],  style={'width': '60%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        html.H2('Selected Zip Code:', style={'textAlign': 'center'}),
        html.H4(id='zip_code', style={'textAlign': 'center'}),
        html.H4(id='schools_table')
    ], style={'width': '40%'})
])

@app.callback(
    Output('map', 'figure'),
    Input('demographic', 'value'))
def display_choropleth(demographic):
    df = zip_means
    geojson = zip_geos
    fig = px.choropleth_mapbox(df, geojson=geojson, color=demographic,
                           locations='Zipcode', featureidkey='properties.ZIPCODE',
                           center={'lat': 40.7128, 'lon': -74.0060},
                           mapbox_style='carto-positron', zoom=9)
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

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
    Output('zip_code', 'children'),
    Input('map', 'clickData'))
def display_zip_code(clickData):
    zip_display = clickData['points'][0]['location']
    return zip_display

@app.callback(
    Output('schools_table', 'children'),
    Input('map', 'clickData'),
    Input('demographic', 'value'))
def display_school_table(clickData, demographic):
    schools2 = schools[schools['Zipcode'] == clickData['points'][0]['location']]
    schools3 = schools2[['School Name', demographic]]
    columns = [{"name": i, "id": i, } for i in schools3.columns]
    df_data = schools3.to_dict('records')

    schooltable = dash_table.DataTable(
        data=df_data,
        columns=columns,
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


# hover barchart
'''
def display_hover(hoverData):
    schools2 = schools[schools['postcode'] == hoverData['points'][0]['location']]
    fig = px.bar(schools2, x='school_name', y='Total Grads % of cohort')
    return fig
'''
app.run_server(debug=True)