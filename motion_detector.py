from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import pymysql
import socket

UDP_IP = '192.168.50.190'
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

log_db = pymysql.connect(
    user='root2',
    password='test',
    host='192.168.50.190',
    database='eventlog',
    charset='utf8'
)

if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)


firstFrame = None
logswitch = False
logswitch2 = False

while True:
    frame_saved = vs.read()
    frame = frame_saved
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"

    if frame is None:
        break

    frame = imutils.resize(frame, width=640)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if firstFrame is None:
        firstFrame = gray.copy().astype("float")
        continue

    cv2.accumulateWeighted(gray, firstFrame, 0.01)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(firstFrame))

    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv2.contourArea(c) < args["min_area"]:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
        text = "Occupied"

    cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] -10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # cv2.imshow("Security Feed", frame)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)

    if text == "Unoccupied":
        logswitch2 = True
        logswitch = False

    if text == "Occupied":
        logswitch = True

    if logswitch == True:
        if logswitch2 == True:
            cursor = log_db.cursor(pymysql.cursors.DictCursor)
            sql = "insert into eventlogtbl (log) values (%s)"
            val = datetime.datetime.now().strftime("%y년%m월%d일%H시%M분%S초")
            cursor.execute(sql, val)
            log_db.commit()

            now = datetime.datetime.now().strftime("%y년%m월%d일%H시%M분-%S초")
            out = cv2.VideoWriter(now + ".avi", cv2.VideoWriter_fourcc(*'DIVX'), 20, (640, 480))

            logswitch2 = False

        out.write(frame_saved)

    streaming = cv2.imencode('.jpg', frame)[1].tobytes()
    for i in range(20):
        sock.sendto(bytes([i]) + streaming[i * 46080:(i + 1) * 46080], (UDP_IP, UDP_PORT))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()