import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime as dt, timedelta as td
from datetime import date

data = []
date1, date2 = None, None


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                children=[
                    html.A(children=html.Img(src="assets/logo-bmstu.svg", width=60, height=60,
                                             style={'margin-bottom': '8px'}), href='https://mf.bmstu.ru/'),
                    html.Div(
                        children=[
                            html.H6("Мытищинский филиал"),
                            html.H4("МГТУ им. Н.Э.Баумана"),
                        ]
                    ),

                ], style={'display': 'flex', 'align-items': 'center'}
            ),
            html.Div(
                children=[
                    html.A(children="webrobo", href="http://webrobo.mgul.ac.ru:3000/"),
                    html.A(children="dbrobo", href="http://dbrobo.mgul.ac.ru/"),
                    html.A(children="dokuwiki", href="http://dokuwiki.mgul.ac.ru/dokuwiki/doku.php"),
                    html.A(children="Github", href='https://github.com/koterevma/monitoring')
                ]
            )
        ]
    )


def build_left_block():
    return html.Div(
        children=[
            "Прибор",
            dcc.Dropdown(id='appliances', multi=True, style={'color': 'black'}),
            "Датчик",
            dcc.Dropdown(id='sensor', multi=True, style={'color': 'black'}),
        ],
        style={'width': '75%', 'display': 'inline-block', 'padding': '10px 0px 30px 40px'}
    )


def build_centre_block():
    return html.Div(
        children=[
            "Осреднение",
            dcc.Dropdown(
                id='rounding',
                options=[
                    {'label': 'без изменений', 'value': 'none'},
                    {'label': '5 минут', 'value': '5min'},
                    {'label': 'осреднять за час', 'value': 'hour'},
                    {'label': 'осреднять за  3 часа', 'value': 'hour3'},
                    {'label': 'осреднять за  сутки', 'value': 'day'},
                    {'label': 'MAX за день', 'value': 'MAX'},
                    {'label': 'MIN за день', 'value': 'MIN'},
                ],
                value='none',
                style={'color': 'black'}
            ),

            "Тип графика",
            dcc.Dropdown(
                id='type',
                options=[
                    {'label': 'линии', 'value': 'lines'},
                    {'label': 'маркеры', 'value': 'markers'},
                    {'label': 'линии + маркеры', 'value': 'lines+markers'},
                    {'label': 'Гистограмма', 'value': 'group'}
                ],
                value='lines',
                style={'color': 'black'}
            ),
        ], style={'width': '75%', 'display': 'inline-block', 'padding': '10px 0px 0px 50px'}
    )


def build_right_block():
    return html.Div(
        children=[
            html.Div(
                [
                    "Промежуток времени",
                    dcc.DatePickerRange(
                        id='date',
                        min_date_allowed=dt(2019, 1, 28),
                        max_date_allowed=date.today(),
                        initial_visible_month=date.today(),
                        start_date=date.today(),
                        end_date=date.today() + td(days=1),
                    ),
                ],

            ),
            html.Div(
                [
                    html.Div(
                        daq.BooleanSwitch(
                            id="Kalman",
                            on=True,
                            label='Фильтр',
                            color='rgb(16,119,94)',
                            labelPosition='top'
                        ),
                        # style={'display': 'inline-block'}
                    ),
                    html.Div(
                        daq.BooleanSwitch(
                            id="Online",
                            on=False,
                            label='API ON/OFF',
                            color='rgb(16,119,94)',
                            labelPosition='top'
                        ),
                        style={'padding': '0px 0px 0px 150px'}
                    ),

                ], style={'display': 'flex'}
            ),

            dcc.Upload(
                # html.Button('Upload File'),
                id='upload'
            ),
        ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px 10px 0px 50px'}
    )


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.config["suppress_callback_exceptions"] = True
app.title = 'BMSTU_Grafics'
app.layout = html.Div(
    children=[
        build_banner(),
        html.Div(
            [
                build_left_block(),
                build_centre_block(),
                build_right_block(),
            ], style={'display': 'flex'}
        ),
        html.Div([dcc.Graph(id='graph',
                            config={
                                "staticPlot": False,
                                "editable": True,
                                "displayModeBar": False,
                            },
                            )], style={'width': '100%', 'padding': '0px 0px 0px 0px'})])


####################################################################
def get_html_page(url):
    html = None
    r = requests.get(url)
    if r.ok:
        html = r.text
    return html


def create_URL(date_begin, date_end):
    return "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/log/{}%2000:00:00/{}%2000:00:00".format(date_begin,
                                                                                                      date_end)


def create_Meteo_URL(date_begin):
    return "https://www.gismeteo.ru/diary/11441/{}/{}/".format(str(date_begin.year), str(date_begin.month), )


def GetMeteo(type_, date_begin, date_end):
    x_arr, y_arr = [], []

    date_begin = dt.strptime(date_begin, '%Y-%m-%d')
    date_end = dt.strptime(date_end, '%Y-%m-%d')
    date_begin = dt(date_begin.year, date_begin.month, 1)
    date_end = dt(date_end.year, date_end.month, 1)

    html = get_html_page(create_Meteo_URL(date_begin))
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    data = table.find('tbody').findAll('tr')
    for row in data:
        day = row.findAll('td')
        x_arr.append(date(date_begin.year, date_begin.month, int(day[0].text)).strftime('%Y-%m-%d'))  # Дата
        if type_ == 'temp':
            y_arr.append((int(day[1].text) + int(day[6].text)) / 2)  # Температура
        else:
            y_arr.append((float(day[2].text) + float(day[7].text)) / 2)  # Давление

    if date_begin != date_end:
        if date_begin.month == 12:
            next_year = date_begin.year + 1
            next_month = 1
            next_day = 1
        else:
            next_year = date_begin.year
            next_month = date_begin.month + 1
            next_day = 1

        newDate = date(next_year, next_month, next_day).strftime('%Y-%m-%d')
        next_x, next_y = GetMeteo(type_, newDate, date_end.strftime('%Y-%m-%d'))
        x_arr.extend(next_x)
        y_arr.extend(next_y)
    return x_arr, y_arr


####################################################################
# def CSV(data, type_):
#     x_arr, y_arr = [], []
#     content_string = data.split(',')
#     # print(content_string)
#     decoded = base64.b64decode(data)
#     # print(decoded)
#     df = csv.reader(io.StringIO(decoded.decode('utf-8')), delimiter=';')
#     next(df)
#     next(df)
#     for item in df:
#         x_arr.append(item[0])
#         if type_ == 'temp':
#             y_arr.append(float(item[1]))
#         else:
#             y_arr.append(float(item[2]))
#     return x_arr, y_arr

####################################################################
def sorting(y_temp, round_):
    if round_ == 'MAX':
        return max(y_temp)
    if round_ == 'MIN':
        return min(y_temp)
    else:
        return sum(y_temp) / len(y_temp)


####################################################################
def Create_date(round_, date):
    New = dt.strptime(date, '%Y-%m-%d %H:%M:%S')
    if round_ == 'day' or round_ == 'MAX' or round_ == 'MIN':
        return dt(New.year, New.month, New.day, 0, 0, 0)
    if round_ == 'hour' or round_ == 'hour3':
        return dt(New.year, New.month, New.day, New.hour, 0, 0)
    if round_ == '5min':
        return dt(New.year, New.month, New.day, New.hour, New.minute, 0)


####################################################################
def how(date_begin, date_end, how):
    if how == "hour" or how == "day" or how == 'MAX' or how == 'MIN':
        return Create_date(how, date_begin) == Create_date(how, date_end)
    if how == "hour3":
        return ((Create_date(how, date_end) - Create_date(how, date_begin)).seconds / 3600) < 3
    if how == "5min":
        return ((Create_date(how, date_end) - Create_date(how, date_begin)).seconds / 60) < 5


####################################################################
def sort(round_, x_arr, y_arr):
    if round_ == "none":
        return x_arr, y_arr
    else:
        x_res, y_res = [], []

        date_begin = x_arr[0]
        y_temp = [y_arr[0]]

        for i in range(1, len(y_arr)):
            date_end = x_arr[i]

            if how(date_begin, date_end, round_):
                y_temp.append(y_arr[i])
            else:
                x_res.append((Create_date(round_, date_begin).strftime('%Y-%m-%d %H:%M:%S')))
                y_res.append(sorting(y_temp, round_))
                date_begin = x_arr[i]
                y_temp = [y_arr[i]]

            if i == len(x_arr) - 1:
                x_res.append((Create_date(round_, date_begin).strftime('%Y-%m-%d %H:%M:%S')))
                y_res.append(sorting(y_temp, round_))

        return x_res, y_res


####################################################################
def create_appliances_list(data):
    temp, res = {}, {}
    for item in data:
        if not "{} ({})".format(data[item]['uName'], data[item]['serial']) in temp:
            temp["{} ({})".format(data[item]['uName'], data[item]['serial'])] = create_devices(data, item)

    sorted_keys = sorted(temp, key=temp.get)
    for i in sorted_keys:
        res[i] = temp[i]

    return res


def create_devices(data, item):
    res = []
    for i in data[item]['data']:
        try:
            float(data[item]['data'][i])
            res.append("{}|{}|{}".format(data[item]['uName'], data[item]['serial'], i))
        except ValueError:
            continue
    return res


def get_info(sensor):
    sensor = sensor.split('|')
    return sensor[0], sensor[1], sensor[2]


def get_data(uName, serial, type):
    x_arr, y_arr = [], []
    for item in data:
        if data[item]['uName'] == uName and data[item]['serial'] == serial:
            try:
                x_arr.append(data[item]['Date'])
                y_arr.append(float(data[item]['data'][type]))

            except ValueError:
                continue

    return x_arr, y_arr


def rounding(x_arr):
    return [round(i, 3) for i in x_arr]

####################################################################
def Kalman_filter(x_arr):
    sPsi = 1
    sEta = 50
    x_opt = [x_arr[0]]
    e_opt = [sEta]

    for i in range(1, len(x_arr)):
        e_opt.append((sEta ** 2 * (e_opt[-1] ** 2 + sPsi ** 2) / (sEta ** 2 + e_opt[-1] ** 2 + sPsi ** 2)) ** 0.5)
        K = e_opt[-1] ** 2 / sEta ** 2
        x_opt.append(K * x_arr[i] + (1 - K) * x_opt[i - 1])

    return x_opt


@app.callback([Output('appliances', 'options'), Output('appliances', 'value')],
              [Input('date', 'start_date'), Input('date', 'end_date'), dash.dependencies.Input('Online', 'on')])
def update_dropdown(start_date, end_date, on):
    global data, date1, date2
    if not data or (date1 != start_date or date2 != end_date):
        date1, date2 = start_date, end_date
    if on:
        data = json.loads(get_html_page(create_URL(start_date, end_date)))

    else:
        with open("log.JSON", 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)

    res = [dict(label=el, value=el) for el in create_appliances_list(data).keys()]

    return res, None


@app.callback([Output('sensor', 'options'), Output('sensor', 'value')],
              [Input('appliances', 'value')])
def update_sensor(appliances):
    res = []
    if appliances is not None:
        for i in appliances:
            lst = create_appliances_list(data)[i]
            for el in lst:
                res.append(dict(label=el, value=el))

    return res, None


####################################################################
@app.callback(Output('graph', 'figure'),
              [Input('sensor', 'value'),
               Input('type', 'value'),
               Input('rounding', 'value'),
               dash.dependencies.Input('Kalman', 'on')])
def update_graph(sensor, type_, round_, filter):
    fig = go.Figure()
    fig.update_layout(
        yaxis=dict(
            titlefont={'color': 'white'},
            title='Значения',
            titlefont_size=16,
            tickfont_size=14,
        ),
        title='',
        showlegend=False,
        autosize=True,
        height=710,
        colorway=['rgb(0,48,255)', 'rgb(0,204,58)', 'rgb(255,154,0)',
                  'rgb(255,0,0)', 'rgb(180,0,210)', 'rgb(0,205,255)', 'rgb(115,90,79)'],

        margin=dict(t=0, b=10, r=40, l=20),
        font_color='white',
        plot_bgcolor='white',
        paper_bgcolor="rgb(75, 75, 83)",

        hoverlabel=dict(
            bgcolor="rgb(75, 75, 83)",
            font_size=16,
            font_family="Rockwell",
        ),
        hovermode="x unified"

    )
    fig.update_xaxes(
<<<<<<< HEAD
        linecolor='black',
        gridcolor='lightgrey',
        zerolinecolor='black',
=======
        linecolor='Gainsboro',
        gridcolor='Gainsboro',
        zerolinecolor='Gainsboro',
>>>>>>> 25fcab734a77cf35e63139af990dd411e04ff6bc
        rangeslider_visible=True,
        # rangeselector=dict(
        #     buttons=list([
        #         dict(count=1, label="1H", step="hour", stepmode="backward"),
        #         dict(count=3, label="3H", step="hour", stepmode="backward"),
        #         dict(count=1, label="1D", step="day", stepmode="todate"),
        #         dict(step="all")
        #     ])
        # )
    ),
    fig.update_yaxes(
<<<<<<< HEAD
        linecolor='black',
        gridcolor='lightgrey',
        zerolinecolor='black',
=======
        linecolor='Gainsboro',
        gridcolor='Gainsboro',
        zerolinecolor='Gainsboro',
>>>>>>> 25fcab734a77cf35e63139af990dd411e04ff6bc
    )

    if sensor is None:
        return fig

    for el in sensor:
        uName, serial, item = get_info(el)

        x_arr, y_arr = get_data(uName, serial, item)

        x_arr, y_arr = sort(round_, x_arr, y_arr)
        if filter:
            y_arr = Kalman_filter(y_arr)
        y_arr = rounding(y_arr)

        if 'group' in type_:
            fig.add_trace(go.Histogram(x=x_arr, y=y_arr, name="{} ({})".format(uName + ' ' + serial, item)))
            fig.update_traces(opacity=0.4)
            # fig.update_traces(opacity=0.4, histnorm="density", histfunc="sum")
            fig.update_layout(barmode='overlay')
        else:
            fig.add_trace(go.Scatter(x=x_arr, y=y_arr, mode=type_, name="{} ({})".format(uName + ' ' + serial, item),
                                     hovertemplate="<b>%{y}</b>"))
    # if round_ == 'day':
    #     temp_x, temp_y = GetMeteo('temp', date1, date2)
    #     fig.add_trace(go.Scatter(x=temp_x, y=temp_y, mode=type_, name="GetMeteo_temp"))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)  # True если надо получать сообщения об ошибках
