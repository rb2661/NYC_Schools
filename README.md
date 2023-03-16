# NYC Schools
 
A dashboard for visualizing data about NYC High Schools, built using Python's Dash library.

A live version of this dashboard can be found at https://rb2661.pythonanywhere.com

This dashboard utilizes data from 5 sources:

1. [NYC Department of Education HS Directory](https://data.cityofnewyork.us/Education/2021-DOE-High-School-Directory/8b6c-7uty)
2. [2016-17 NYC Graduation Outcomes by School](https://data.cityofnewyork.us/Education/2016-2017-Graduation-Outcomes-School/nb39-jx2v)
3. [2013-2018 NYC Demographic School Snapshots](https://data.cityofnewyork.us/Education/2013-2018-Demographic-Snapshot-School/s52a-8aq6)
4. [GeoJSON file of NYC School Districts](https://data.cityofnewyork.us/Education/School-Districts/r8nu-ymqj)
5. [GeoJSON file of NYC Zip Codes](https://data.cityofnewyork.us/widgets/i8iw-xf4u)

All files can be found at the NYC Open Data links provided.

I chose to utilize pre-pandemic data because I wanted to get a sense of how each variable was trending without the disruption of the external factor of COVID-19.

How to use this dashboard:

Utilize the drop-down menu to select a demographic variable related to NYC High Schools that you're interested in investigating. Select a year from the radio buttons to see data specific to that year.

Hovering your mouse on the map gives you the identifying School District or Zip Code and the associated statistic for High Schools in that regopm, in the given year.

Clicking on a region populates a line graph and table on the right-hand side of the dashboard. The line graph illustrates data for each school in the given region, over all 5 years of data in the dashboard. The table highlights the value of the chosen variable of interest only for each school, only on the year chosen in the radio buttons.
