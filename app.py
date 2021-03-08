#import pandas as pd
import urllib.request, json 
from datetime import datetime
from collections import deque

import dash
import plotly
import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def parse_iss_loc(iss_url = 'http://api.open-notify.org/iss-now.json'):
    with urllib.request.urlopen(iss_url) as url:
        data = json.loads(url.read().decode())

    if data['message'] == 'success':
        date = datetime.fromtimestamp(data['timestamp'])
        loc_info = {'latitude': data['iss_position']['latitude'],
                    'longitude': data['iss_position']['longitude'],
                    'time': date.strftime('%Y-%b-%d-%H-%M-%S')}
        return loc_info
    else:
        print("Failed to retrieve the ISS location data")
        return None

def main(retrieve_inter = 1):
    """
    Retrieve the location every "retrieve_inter" milliseconds
    """
    maxlen = int(90*60/retrieve_inter) #the full cycle time of ISS is 90 minutes
    X = deque(maxlen=maxlen)
    Y = deque(maxlen=maxlen)
    fig = go.Figure() #define the figure for dash

    app = dash.Dash()
    app.layout = html.Div(children = [
        html.H1(children = 'Real Time ISS Location'),
        html.Table([html.Tr([html.Td('Time'), html.Td(id='live-time')])]),
        dcc.Graph(id = 'live-coor', figure = fig),
        dcc.Interval(id = 'geo-update', interval=retrieve_inter*1000) #convert to milliseconds
    ])

    @app.callback(Output(component_id='live-coor', component_property='figure'),
                  Output(component_id='live-time', component_property='children'),
                  Input(component_id='geo-update', component_property='n_intervals'))
    def update_graph(input_data):
        loc_info = None
        time_string = None
        while loc_info is None:
            loc_info = parse_iss_loc()
            X.append(loc_info['longitude'])
            Y.append(loc_info['latitude'])
            time_string = loc_info['time']
        
        new_fig = go.Figure(data = go.Scattergeo(lon = list(X), lat = list(Y), mode = 'lines+markers'))
        return new_fig, time_string

    app.run_server(debug=True)

if __name__ == '__main__':
    main()