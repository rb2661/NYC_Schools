import pandas as pd
import geopandas as gpd

# dataset containing all high schools in NYC
schools = pd.read_csv('data/2021_DOE_High_School_Directory.csv')

schools = schools[['dbn', 'school_name', 'Borough', 'Latitude', 'Longitude', 'url', 'total_students', 'graduation_rate',
                   'attendance_rate', 'NTA', 'postcode']]

# update Gotham DBN, so it joins to the other 2 data sets
schools.loc[schools['school_name'] == 'Gotham Professional Arts Academy', 'dbn'] = '16K594'

# update arts academy zip code
schools.loc[schools['school_name'] == 'Art and Design High School', 'postcode'] = '10022'

# grad rates data -- much more complete than the original data
schools_grad = pd.read_csv('data/2016-2017_Graduation_Outcomes_School.csv')

# filtering to only graduation statistics for 4-year graduation rates for all students
cohort_mask = schools_grad['Cohort'] == '4 year June'
year_mask = schools_grad['Cohort Year'] >= 2009
type_mask = schools_grad['Demographic Category'] == 'All Students'

schools_grad2 = schools_grad[cohort_mask][year_mask][type_mask]

# join
schools_full = schools.merge(schools_grad2, left_on='dbn', right_on='DBN')

schools_demo = pd.read_csv('data/2013_-_2018_Demographic_Snapshot_School.csv')

# changing year format to be joinable
schools_demo['Year'] = schools_demo['Year'].str[:-3]

schools_demo['Year'] = schools_demo['Year'].apply(pd.to_numeric)

schools_full['Cohort Year'] = schools_full['Cohort Year'] + 4

schools_full2 = schools_full.merge(schools_demo, left_on=['dbn', 'Cohort Year'], right_on=['DBN', 'Year'])

schools_full2['postcode'] = schools_full2['postcode'].apply(lambda x: str(x).replace(",", ""))

schools_final = schools_full2[['dbn', 'school_name', 'Borough', 'Latitude', 'Longitude', 'url', 'total_students',
                               'graduation_rate', 'attendance_rate', 'NTA', 'postcode', 'Cohort Year', 'Total Cohort #',
                               'Total Grads #', 'Total Grads % of cohort', '# Female', '% Female', '# Male', '% Male',
                               '# Asian', '% Asian', '# Black', '% Black', '# Hispanic', '% Hispanic', '# Poverty',
                               '% Poverty']]

# importing geojson containing nyc zip code geographic data

nyc_zip = gpd.read_file('data/zip_code_040114.geojson')
nyc_zip = nyc_zip[['ZIPCODE', 'geometry']]

zips = nyc_zip['ZIPCODE'].value_counts()

# Some zip code polygons have duplicate rows. I kept the first row for each that appeared.
nyc_zip.drop([109, 113, 114, 146, 149, 259, 27, 28, 123, 246, 19, 253, 241, 194, 144], inplace=True)

nyc_geo = nyc_zip.merge(schools_final, how='outer', left_on='ZIPCODE', right_on='postcode')

# nyc_geo.ZIPCODE.value_counts().plot(kind='barh', figsize=(20,16))

# creating dataframe containing mean values for schools in the same zip code
# this aggregate data will allow for choropleth mapping
mean_values = nyc_geo[['ZIPCODE', 'Cohort Year', 'Total Cohort #', 'Total Grads #', 'Total Grads % of cohort',
                       '# Female', '% Female', '# Male', '% Male', '# Asian', '% Asian', '# Black', '% Black',
                       '# Hispanic', '% Hispanic', '# Poverty', '% Poverty']].groupby(['ZIPCODE', 'Cohort Year']).mean()

cols = ['mean cohort #', 'mean grad #', 'mean grad %', 'mean female #', 'mean female %', 'mean male #', 'mean male %',
        'mean asian #', 'mean asian %', 'mean black #', 'mean black %', 'mean hispanic #', 'mean hispanic %',
        'mean poverty #', 'mean poverty %']

mean_values.columns = cols
mean_values = mean_values.reset_index()

zip_means = nyc_geo[['ZIPCODE', 'geometry']].merge(mean_values, left_on='ZIPCODE', right_on='ZIPCODE')

zip_means.drop_duplicates(inplace=True)

zip_means_gdf = gpd.GeoDataFrame(zip_means, crs='EPSG:4326', geometry=zip_means.geometry)

zip_geos = zip_means_gdf[['ZIPCODE', 'geometry']]

# save dataframes into csv files for use in app.py
zip_new_cols = ['Zipcode', 'geometry', 'Cohort Year', 'Graduating Cohort', 'Graduates', 'Graduation Rate',
                'Female Student Count', 'Female %', 'Male Student Count', 'Male %',
                'Asian Student Count', 'Asian %', 'Black Student Count', 'Black %',
                'Hispanic Student Count', 'Hispanic %', 'Students in Poverty Count', 'Poverty %']

zip_means.columns = zip_new_cols

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

# Art and Design High School -- wrong postal code: change from 10019 to 10022
# Eagle Academy for Young Men of Staten Island, The - no data in grad rate dataset
# Gotham Professional Arts Academy - (change dbn from 13K594 to 16K594 in original dataset so that it gets joined)
# Epic High School - South - no data in grad rate dataset
