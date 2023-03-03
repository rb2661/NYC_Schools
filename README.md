# NYC Schools
 
A dashboard for visualizing data about NYC High Schools.

A live version of this dashboard can be found at https://rb2661.pythonanywhere.com

This dashboard utilizes data from 4 sources:

1. NYC Department of Education HS Directory
2. 2016-17 NYC Graduation Outcomes by School
3. 2013-2018 NYC Demographic School Snapshots
4. GeoJSON file of NYC Zip Codes

The first 3 files can all be found on NYC Open Data.

I chose to utilize pre-pandemic data because I wanted to get a sense of how each variable was trending without the disruption of the external factor of COVID-19.

How to use this dashboard:

Utilize the drop-down menu to select a demographic variable related to NYC High Schools that you're interested in investigating. Select a year from the radio buttons to see data specific to that year.

Hovering your mouse on the map gives you the Zip Code numbers and the associated statistic for High Schools in that Zip Code, in the given year.

Clicking on a Zip Code populates a line graph and table on the right-hand side of the dashboard. The line graph illustrates data for each school in the given Zip Code, over all 5 years of data in the dashboard. The table highlights the value of the chosen variable of interest only for each school, only on the year chosen in the radio buttons.
