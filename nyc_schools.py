import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from dash import Dash, html, dcc

schools = pd.read_csv('data/2021_DOE_High_School_Directory.csv')

# columns we're interested in:
# dbn, school_name, Borough, postcode, latitude, longitude, url, total_students, graduation_rate, attendance_rate, NTA, postcode

schools = schools[['dbn', 'school_name', 'Borough', 'Latitude', 'Longitude', 'url', 'total_students', 'graduation_rate', 'attendance_rate', 'NTA', 'postcode']]


# update Gotham DBN so it joins to the other 2 data sets
schools.loc[schools['school_name'] == 'Gotham Professional Arts Academy', 'dbn'] = '16K594'

# update arts academy zip code
schools.loc[schools['school_name'] == 'Art and Design High School', 'postcode'] = '10022'

# grad rates data -- much more complete than the original data
schools_grad = pd.read_csv('data/2016-2017_Graduation_Outcomes_School.csv')

cohort_mask = schools_grad['Cohort'] == '4 year June'
year_mask = schools_grad['Cohort Year'] >= 2009
type_mask = schools_grad['Demographic Category'] == 'All Students'

schools_grad2 = schools_grad[cohort_mask][year_mask][type_mask]

# join

schools_full = schools.merge(schools_grad2, left_on='dbn', right_on='DBN')

schools_demo = pd.read_csv('data/2013_-_2018_Demographic_Snapshot_School.csv')

#year_mask2 = schools_demo['Year'] == '2016-17'

#schools_demo2 = schools_demo[year_mask2]

#changing year format to be joinable
schools_demo['Year'] = schools_demo['Year'].str[:-3]

schools_demo['Year'] = schools_demo['Year'].apply(pd.to_numeric)

schools_full['Cohort Year'] = schools_full['Cohort Year'] + 4

schools_full2 = schools_full.merge(schools_demo, left_on=['dbn', 'Cohort Year'], right_on=['DBN', 'Year'])

fig = px.scatter(schools_full2, x='Total Grads % of cohort', y='% Poverty', size='Total Cohort #', color='Borough')

#fig.show()

fig2 = px.histogram(schools_full2, x='Total Cohort #', y='% Asian', histfunc='avg', nbins=20)

#fig2.show()

schools_full2['postcode'] = schools_full2['postcode'].apply(lambda x: str(x).replace(",", ""))

schools_final = schools_full2[['dbn', 'school_name', 'Borough', 'Latitude', 'Longitude', 'url', 'total_students',
                               'graduation_rate', 'attendance_rate', 'NTA', 'postcode', 'Cohort Year', 'Total Cohort #',
                               'Total Grads #', 'Total Grads % of cohort', '# Female', '% Female', '# Male', '% Male',
                               '# Asian', '% Asian', '# Black', '% Black', '# Hispanic', '% Hispanic', '# Poverty',
                               '% Poverty']]

# zip codes geojson

nyc_zip = gpd.read_file('data/zip_code_040114.geojson')
nyc_zip = nyc_zip[['ZIPCODE', 'geometry']]

zips = nyc_zip['ZIPCODE'].value_counts()

nyc_zip.drop([109, 113, 114, 146, 149, 259, 27, 28, 123, 246, 19, 253, 241, 194, 144], inplace=True)

"""I have no idea which zip code polygons are correct for the duplicate rows. I'm just going to keep the first of each and can modify if they look wrong.

10004: Keep 106, drop 109, 113, 114

11693: Keep 134, drop 146, 149, 259

10464: Keep 16, drop 27, 28

11231: Keep 118, drop 123

10047: Keep 245, drop 246

10463: Keep 14, drop 19

10035: Keep 49, drop 253

10196: Keep 240, drop 241

11370: Keep 65, drop 194

11096: Keep 139, drop 144

"""

nyc_geo = nyc_zip.merge(schools_final, how='outer', left_on='ZIPCODE', right_on='postcode')

nyc_geo.ZIPCODE.value_counts().plot(kind='barh', figsize=(20,16))

mean_values = nyc_geo[['ZIPCODE', 'Cohort Year', 'Total Cohort #', 'Total Grads #', 'Total Grads % of cohort', '# Female', '% Female',
       '# Male', '% Male', '# Asian', '% Asian', '# Black', '% Black', '# Hispanic', '% Hispanic', '# Poverty', '% Poverty']].groupby(['ZIPCODE', 'Cohort Year']).mean()

cols = ['mean cohort #', 'mean grad #', 'mean grad %', 'mean female #', 'mean female %', 'mean male #', 'mean male %', 'mean asian #', 'mean asian %',
        'mean black #', 'mean black %', 'mean hispanic #', 'mean hispanic %', 'mean poverty #', 'mean poverty %']

mean_values.columns = cols
mean_values = mean_values.reset_index()

zip_means = nyc_geo[['ZIPCODE', 'geometry']].merge(mean_values, left_on = 'ZIPCODE', right_on = 'ZIPCODE')

zip_means.drop_duplicates(inplace=True)

zip_means_gdf = gpd.GeoDataFrame(zip_means, crs='EPSG:4326', geometry=zip_means.geometry)

zip_geos = zip_means_gdf[['ZIPCODE', 'geometry']]

def popup_html(row):
    i = row
    school_name = schools_final['school_name'].iloc[i]
    school_size = schools_final['total_students'].iloc[i]
    grad_cohort = schools_final['Total Grads #'].iloc[i]
    grad_pct = schools_final['Total Grads % of cohort'].iloc[i]
    gender = schools_final['% Female'].iloc[i]
    asian = schools_final['% Asian'].iloc[i]
    black = schools_final['% Black'].iloc[i]
    hispanic = schools_final['% Hispanic'].iloc[i]
    url = schools_final['url'].iloc[i]

    left_col_color = "#73A5C6"
    right_col_color = "#f2f9ff"
    
    html = """
<!DOCTYPE html>
<html>
<center><h4 style="margin-bottom:5"; width="200px">{}</h4>""".format(school_name) + """</center>
<center><a href=\"""" + url + """\">View School Profile</a></center>
<center> <table style="height: 126px; width: 225px;">
<tbody>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Current School Size (2021) </span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>"""+school_size +"""</td></center>
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Graduating Class Size (2017) </span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(grad_cohort) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Graduation Rate (2017) (%) </span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(grad_pct) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Female (%) </span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(gender) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Asian (%)</span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(asian) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Black (%)</span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(black) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"> Hispanic (%)</span></td>
<td style="width: 50px;background-color: """+ right_col_color +""";"><center>{}</td></center>""".format(hispanic) + """
</tr>
</tbody>
</table></center>
</html>
"""
    return html

# new choropleth map
coords = [40.7128, -74.0060]

nyc_zip_map = folium.Map(coords, tiles='OpenStreetMap', zoom_start = 12)

folium.Choropleth(
    geo_data = zip_geos,
    name = 'Zip Codes',
    data = zip_means,
    columns = ['ZIPCODE', 'mean grad #'],
    key_on = 'feature.id',
    fill_color = 'YlGnBu',
    fill_opacity = 0.5,
    line_opacity = 1,
    legend_name = 'Mean Graduating Class Size',
    smooth_factor = 0
).add_to(nyc_zip_map)

#fg = folium.FeatureGroup('School Locations').add_to(nyc_zip_map)

marker_cluster = MarkerCluster(name='School Locations').add_to(nyc_zip_map)

for i in range(0,len(schools_final)):

  #popup 
  html = popup_html(i)
  popup = folium.Popup(folium.Html(html, script=True), max_width=500)

  marker_cluster.add_child(folium.Marker(
      location=[schools_final.iloc[i]['Latitude'], schools_final.iloc[i]['Longitude']],
      popup=popup,
      icon=folium.Icon(icon='mortar-board', prefix='fa')
  )).add_to(nyc_zip_map)

folium.LayerControl().add_to(nyc_zip_map)

#nyc_zip_map.save("figures/nyc_zip_map.html")
#webbrowser.open("figures/nyc_zip_map.html")

# save dataframes into csv files for use in app.py

#print(zip_means.columns)

zip_new_cols = ['Zipcode', 'geometry', 'Cohort Year', 'Graduating Cohort', 'Graduates', 'Graduation Rate',
                'Female Student Count', 'Female %', 'Male Student Count', 'Male %',
                'Asian Student Count', 'Asian %', 'Black Student Count', 'Black %',
                'Hispanic Student Count', 'Hispanic %', 'Students in Poverty Count', 'Poverty %']

zip_means.columns = zip_new_cols

#print(schools_final.columns)

schools_new_cols = ['dbn', 'School Name', 'Borough', 'Latitude', 'Longitude', 'url',
                    'Total Students', '2021 Grad Rate', '2021 Attendance Rate', 'NTA',
                    'Zipcode', 'Cohort Year', 'Graduating Cohort', 'Graduates', 'Graduation Rate',
                'Female Student Count', 'Female %', 'Male Student Count', 'Male %',
                'Asian Student Count', 'Asian %', 'Black Student Count', 'Black %',
                'Hispanic Student Count', 'Hispanic %', 'Students in Poverty Count', 'Poverty %']

schools_final.columns = schools_new_cols

zip_means.to_csv('data/zip_means.csv')
schools_final.to_csv('data/schools_final.csv')

zip_geos.to_file('data/zip_geos.json', driver='GeoJSON')

# testing px.choropleth


# Art and Design High School -- wrong postal code: change from 10019 to 10022
# Eagle Academy for Young Men of Staten Island, The - no data in grad rate dataset
# Gotham Professional Arts Academy - wrong DBN number in original dataset (change from 13K594 to 16K594 in original dataset so that it gets joined)
# Epic High School - South - no data in grad rate dataset