import socket
import cv2

UDP_IP = '193.123.234.179'
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    streaming= cv2.imencode('.jpg', frame)[1].tobytes()

    for i in range(20):
        sock.sendto(bytes([i]) + streaming[i * 46080:(i + 1) * 46080], (UDP_IP, UDP_PORT))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break