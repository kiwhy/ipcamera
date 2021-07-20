import socket
import numpy
import cv2
from flask import Flask, render_template, Response

UDP_IP = "192.168.50.190"
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

app = Flask(__name__)

s = [b'\xff' * 46080 for x in range(20)]

@app.route('/')
def index():
    "video streaming"
    return render_template('streaming.html')

def streaming():
    while True:
        picture = b''

        data, addr = sock.recvfrom(46081)
        s[data[0]] = data[1:46081]

        if data[0] == 19:
            for i in range(20):
                picture += s[i]

            frame = picture
            # frame = frame.reshape(640, 480, 3)
            # frame = frame.tobytes()

            yield (b'--frame\r\n'
                   b'content-type: image/jpg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(1) & 0xFF == ord('q'):
           cv2.destroyAllWindows()
           break

@app.route('/video_feed')
def video_feed():
    return Response(streaming(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)