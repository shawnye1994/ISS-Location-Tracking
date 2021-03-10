##https://community.plotly.com/t/does-dash-support-opencv-video-from-webcam/11012/2

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from flask import Flask, Response
import cv2
from collections import deque

class VideoCamera(object):
    """
    Cache some frames for the beackend processing
    """
    def __init__(self, cache_len = 3):
        self.video = cv2.VideoCapture(0)
        self.cache_frames = deque(maxlen = cache_len)
        self.frame_id = 0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        self.frame_id += 1
        self.cache_frames.append((image, self.frame_id)) #cahche frames
        
        image = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2))
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
    
    def get_caches(self):
        return list(self.cache_frames)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def main(retrieve_inter = 0.2):
    server = Flask(__name__)
    app = dash.Dash(__name__, server=server)
    live_cam = VideoCamera()

    @server.route('/video_feed')
    def video_feed():
        return Response(gen(live_cam),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    app.layout = html.Div([
        html.H1("Webcam Test"),
        html.Table([html.Tr([html.Td('Frames'), html.Td(id='frame_count')])]),
        html.Img(id = 'cam', src="/video_feed"),
        dcc.Interval(id = 'vid_process', interval=retrieve_inter*1000) #convert to milliseconds
    ])

    @app.callback(Output(component_id='frame_count', component_property='children'),
                  Input(component_id='vid_process', component_property='n_intervals'))
    def process_vid(inptu_data):
        cache_frames = live_cam.get_caches()
        frames_string = ""
        for cache in cache_frames:
            f, c = cache
            print(f.shape)
            print(c)
            frames_string += str(c) + ','
        return frames_string
        
    app.run_server(debug=True)

if __name__ == '__main__':
    main()