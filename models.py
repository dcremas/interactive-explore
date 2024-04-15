import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv('PG_DB')
user = os.getenv('PG_USERNAME')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
port =os.getenv('PG_PORT')
          
url_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

stations_input = ['70381025309',
                   '72290023188',
                   '72530094846',
                   '72494023234',
                   '72565003017',
                   '91182022521',
                   '72509014739',
                   '72606014764',
                   '72306013722',
                   '74486094789']

stations_tuple = tuple(stations_input)

query_stations = f'''
SELECT DISTINCT loc.station_name
FROM locations loc
JOIN observations obs
    ON loc.station = obs.station
JOIN regions rgn
    ON loc.state = rgn.state
WHERE obs.station IN {stations_tuple}
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
WHERE obs.station IN {stations_tuple}
    AND EXTRACT(YEAR from obs.date) BETWEEN 2020 AND 2024
    AND obs.report_type IN ('FM-15')
    AND obs.slp BETWEEN 20.00 AND 35.00
    AND obs.prp <= 10.00
ORDER BY obs.station, obs.date;
'''

query_update = f'''
SELECT
MAX(timestamp)
FROM observations;
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
    cursor.execute(query_update)
    response_update = cursor.fetchall()
    time_update = response_update[0][0]
