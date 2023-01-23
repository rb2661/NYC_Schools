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
        html.P('Select a demographic and year:'),
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
    ], style={'width': '60%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='map')
    ],  style={'width': '60%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='time-series')
    ], style={'display': 'inline-block', 'float': 'right', 'width': '40%'}),
    html.Div([
        html.H2('Selected Zip Code:', style={'textAlign': 'center'}),
        html.H4(id='zip_code', style={'textAlign': 'center'}),
        html.H4(id='schools_table')
    ], style={'width': '40%'})
])

@app.callback(
    Output('map', 'figure'),
    Input('demographic', 'value'),
    Input('year', 'value'))
def display_choropleth(demographic, year):
    df = zip_means[zip_means['Cohort Year'] == year]
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
    Input('demographic', 'value'),
    Input('year', 'value'))
def display_school_table(clickData, demographic, year):
    schools2 = schools[schools['Zipcode'] == clickData['points'][0]['location']]
    schools3 = schools2[schools2['Cohort Year'] == year]
    schools4 = schools3[['School Name', demographic]]
    columns = [{"name": i, "id": i, } for i in schools4.columns]
    df_data = schools4.to_dict('records')

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

@app.callback(
    Output('time-series', 'figure'),
    Input('map', 'clickData'),
    Input('demographic', 'value'))
def time_series_plot(clickData, demographic):
    schools2 = schools[schools['Zipcode'] == clickData['points'][0]['location']]
    schools3 = schools2[['School Name', 'Cohort Year', demographic]]
    schools4 = schools3.sort_values(by=['School Name', 'Cohort Year'], ascending=[True, True])
    fig = px.line(schools4, x='Cohort Year', y=demographic, color='School Name',
                  title='School Demographics by Year', markers=True)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(nticks=5)
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left', text='')

    fig.update_layout(height=500, margin={'l': 10, 'b': 10, 'r': 10, 't': 40})

    return fig
# hover barchart
'''
def display_hover(hoverData):
    schools2 = schools[schools['postcode'] == hoverData['points'][0]['location']]
    fig = px.bar(schools2, x='school_name', y='Total Grads % of cohort')
    return fig
'''
app.run_server(debug=True)