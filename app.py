from os.path import dirname, join
from pathlib import Path

import psycopg2
import pandas as pd
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Range1d, Paragraph
from bokeh.plotting import figure

from models import stations, data, headers, time_update

weatherdata = pd.DataFrame(data, columns=headers)
weatherdata['date'] = np.array(weatherdata['date'], dtype=np.datetime64)

axis_map = {
    "Temperature": "tmp",
    "Barometric Pressure": "slp",
    "Wind Speed": "wnd",
    "Dew Point": "dew",
}

y_axis_range = {
    "Temperature": (-25.0, 125.0), 
    "Barometric Pressure": (28.5, 31.5),
    "Wind Speed": (0.0, 50.0),
    "Precipitation": (0.0, 1.0),
    "Dew Point": (0.0, 100.0),
}

desc = Div(text=(Path(__file__).parent / "description.html").read_text("utf8"), sizing_mode="stretch_width",
           margin=(2, 2, 2, 15))

years = Slider(title="Year", value=2021, start=2021, end=2025, step=1, margin=(2, 2, 2, 15))
months = Slider(title="Month", value=1, start=1, end=12, step=1, margin=(2, 2, 2, 15))
station_name = Select(title="Weather Station Name", value=stations[0], options=stations, margin=(2, 2, 2, 15))
y_axis = Select(title="Main Chart Y Axis", options=sorted(axis_map.keys()), value="Barometric Pressure", margin=(2, 2, 2, 15))

source = ColumnDataSource(data=dict(x=weatherdata[weatherdata['station_name'] == stations[0]]['date'],
                                    y=weatherdata[weatherdata['station_name'] == stations[0]][axis_map[y_axis.value]]))

plot = figure(height=400, title="", toolbar_location=None, sizing_mode="stretch_width",
              x_axis_type="datetime", y_range=y_axis_range[y_axis.value], margin=(10, 10, 10, 15),
              background_fill_color="#feffd9", outline_line_color='white')

plot.line(x="x", y="y", source=source)

source_precip = ColumnDataSource(data=dict(x=weatherdata[weatherdata['station_name'] == stations[0]]['date'],
                                    y=weatherdata[weatherdata['station_name'] == stations[0]]['prp']))

plot_precip = figure(height=150, width=400, title="", toolbar_location=None, sizing_mode="stretch_width",
              x_axis_type="datetime", y_range=y_axis_range['Precipitation'], margin=(10, 10, 10, 15),
              background_fill_color="#e8eafa", outline_line_color='white')

plot_precip.vbar(x="x", top="y", source=source_precip)
plot_precip.yaxis.axis_label = "Precip"


def select_weather_records():
    selected = weatherdata[
        (weatherdata.rdg_year == years.value) &
        (weatherdata.rdg_month == months.value) &
        (weatherdata.station_name == station_name.value)
    ]
    return selected


def update():
    df = select_weather_records()
    y_name = axis_map[y_axis.value]
    plot.yaxis.axis_label = y_axis.value
    y_range_min = y_axis_range[y_axis.value][0]
    y_range_max = y_axis_range[y_axis.value][1]
    plot.y_range.update(start=y_range_min, end=y_range_max)
    source.data = dict(
        x=df['date'],
        y=df[y_name],
    )
    source_precip.data = dict(
        x=df['date'],
        y=df['prp'],
    )

controls = [years, months, station_name, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

update_text_1 = f'The Postgresql AWS Cloud Database that feeds the visuals was last updated:'
update_text_2 = f'Date: {time_update.strftime("%d %B, %Y")}'
update_text_3 = f'Time: {time_update.strftime("%I:%M:%S %p")}'

p1 = Paragraph(text=update_text_1, width=800, height=10, margin=(25, 25, 5, 15))
p2 = Paragraph(text=update_text_2, width=800, height=10, margin=(5, 25, 5, 15))
p3 = Paragraph(text=update_text_3, width=800, height=10, margin=(5, 25, 25, 15))

hyperlink_github = Div(
    text="""<p><i>To see the full codebase for this interactive web-based visualization: </i><a href="https://github.com/dcremas/interactive-explore">Link to my github account</a></p>""",
    width=800, height=25, margin=(10, 10, 10, 15)
    )

hyperlink_div = Div(
    text="""<a href="https://dataviz.dustincremascoli.com">Go back to Data Visualizations Main Page</a>""",
    width=400, height=100, margin=(10, 10, 10, 15)
    )

layout = column(desc,
                hyperlink_github, 
                row(years, months, sizing_mode="inherit"),
                station_name,
                y_axis,
                plot,
                plot_precip,
                p1,
                p2,
                p3,
                hyperlink_div,
                sizing_mode="stretch_width", height=400)

update()

curdoc().add_root(layout)
curdoc().title = "Historical Hourly Weather Data"
