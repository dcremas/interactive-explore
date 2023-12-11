import psycopg2
          
dbname = 'weatherdata'
user = 'dustincremascoli'
password = 'mp2BrVcin8chgfxUO7vb'
host = 'db-aws.cu1h5zzynwdo.us-east-2.rds.amazonaws.com'
port = 5432

url_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

query_stations = f'''
SELECT DISTINCT loc.station_name
FROM locations loc
JOIN observations obs
    ON loc.station = obs.station
JOIN regions rgn
    ON loc.state = rgn.state
WHERE rgn.sub_region IN ('PACIFIC', 'EAST NORTH CENTRAL', 'NEW ENGLAND')
ORDER BY loc.station_name;
'''

query_data = f'''
SELECT
    obs.station,
    loc.station_name,
    loc.state,
    obs.date,
    EXTRACT(YEAR from obs.date) AS rdg_year,
    EXTRACT(MONTH from obs.date) AS rdg_month,
    EXTRACT(DAY from obs.date) AS rdg_day,
    obs.tmp,
    obs.slp,
    obs.wnd,
    obs.prp,
    obs.dew
FROM observations obs
JOIN locations loc
    ON obs.station = loc.station
JOIN regions rgn
    ON loc.state = rgn.state
WHERE rgn.sub_region IN ('PACIFIC', 'EAST NORTH CENTRAL', 'NEW ENGLAND')
    AND EXTRACT(YEAR from obs.date) BETWEEN 2022 AND 2023
    AND obs.source IN ('6', '7')
    AND obs.report_type IN ('FM-15')
    AND obs.slp BETWEEN 20.00 AND 35.00
    AND obs.prp <= 10.00
ORDER BY obs.station, obs.date;
'''

headers = ['station' , 'station_name', 'state', 'date', 'rdg_year', 'rdg_month', 'rdg_day', 'tmp', 'slp', 'wnd', 'prp', 'dew']

with psycopg2.connect(url_string) as connection:
    cursor = connection.cursor()
    cursor.execute(query_stations)
    response_stations = cursor.fetchall()
    stations = [x[0] for x in response_stations]
    cursor.execute(query_data)
    response_data = cursor.fetchall()
    data = [x for x in response_data]
