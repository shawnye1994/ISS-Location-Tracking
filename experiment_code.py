#import pandas as pd
import urllib.request, json 
from datetime import datetime
from collections import deque

import dash
import plotly
import plotly.graph_objs as go
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
                    'time': date.strftime('%Y-%b-%d-%H-%S')}
        return loc_info
    else:
        print("Failed to retrieve the ISS location data")
        return None

def main():
    X = deque(maxlen=30)
    Y = deque(maxlen=30)
    app = dash.Dash()
    app.layout = html.Div(children = [
        html.H1(children = 'Real Time ISS Location'),
        dcc.Graph(id = 'live-coor', animate=True),
        dcc.Interval(id = 'geo-update', interval=1*1000) #1 second
    ])

    @app.callback(Output(component_id='live-coor', component_property='figure'),
                  Input(component_id='geo-update', component_property='n_intervals'))
    def update_graph(input_data):
        loc_info = None
        while loc_info is None:
            loc_info = parse_iss_loc()
            X.append(loc_info['longitude'])
            Y.append(loc_info['latitude'])
        
        data = plotly.graph_objs.Scatter(x = list(X), y = list(Y), name = 'scatter', mode = 'lines+markers')
        
        return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis=dict(range=[min(Y),max(Y)]))}
    
    app.run_server(debug=True)

if __name__ == '__main__':
    main()