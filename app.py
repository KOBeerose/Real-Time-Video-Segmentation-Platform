from sys import stdout
from makeup_artist import Makeup_artist
import logging
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from camera import Camera
from utils import base64_to_pil_image, pil_image_to_base64
import cv2
import numpy as np
import base64
import io
import imageio
from imageio import imread
import os 

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
camera = Camera(Makeup_artist())

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

detector = cv2.CascadeClassifier("./Haarcascades/haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("./Haarcascades/haarcascade_eye.xml")


@socketio.on('input image', namespace='/test')
def test_message(input):
    input = input.split(",")[1]
    camera.enqueue_input(input)
    image_data = input # Do your magical Image processing here!!

    img = imread(io.BytesIO(base64.b64decode(image_data)))
    image_np = np.array(img)
    frame = image_np
    
    color =  cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    print(get_immediate_subdirectories("./"))
    faces = detector.detectMultiScale(color, 1.3, 5)
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("reconstructed.jpg", gray)
    # Draw the rectangle around each faces
    for (x, y, w, h) in faces:
        cv2.rectangle(color, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # roi_gray = gray[y:y+h, x:x+w]
        roi_color = color[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_color, 1.8, 5)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    ret,buffer=cv2.imencode('.jpg',color)
    b = base64.b64encode(buffer)
    b = b.decode()
    image_data = "data:image/jpeg;base64," + b

    # print("OUTPUT " + image_data)
    emit('out-image-event', {'image_data': image_data}, namespace='/test')
    #camera.enqueue_input(base64_to_pil_image(input))


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/home')
def home():
    """Video streaming home page."""
    return render_template('home.html')


def generate_frames():
    app.logger.info("starting to generate frames!")
    while True:
            
        ## read the camera frame
        frame = camera.get_frame()
        print(type(frame))
        success = True
        print("I am outside")
        if not success:
            print("I am if")
            print(frame)
        else:
            print(type(frame))
            print("I am else")
            faces = detector.detectMultiScale(frame, 1.1, 7)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Draw the rectangle around each faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen():
    """Video streaming generator function."""

    app.logger.info("starting to generate frames!")
    while True:
        frame = camera.get_frame() #pil_image_to_base64(camera.get_frame())

        print(type(frame))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_test')
def video_test():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/test')
def test():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app)
