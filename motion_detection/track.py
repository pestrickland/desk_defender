"""`track` uses background subtraction to detect moving targets."""
import cv2
import time
import argparse
import datetime
import imutils
import gdrive
import tempimg



def main():

    parser = argparse.ArgumentParser("Configure image tracker.",
                                     parents=[gdrive.FLAGS])
    parser.add_argument("-u", "--upload", help="upload images to Google Drive",
                        action="store_true")
    parser.add_argument("-l", "--live", help="show live output",
                        action="store_true")
    args = parser.parse_args()

    try:
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        camera = PiCamera()
        camera.resolution = (640, 480)

    except ImportError:
        camera = cv2.VideoCapture(0)

    camera.framerate = 15
    rawCapture = PiRGBArray(camera, size=(640, 480))
    avg = None
    print("[INFO] warming up...")
    time.sleep(2.5)
    avg = None
    lastUploaded = datetime.datetime.now()
    motionCounter = 0

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = f.array
        timestamp = datetime.datetime.now()
        text = "Unoccupied"
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if avg is None:
            print("[INFO] starting background model...")
            avg = gray.copy().astype("float")
            rawCapture.truncate(0)
            continue
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, 5, 255,
            cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (dummy, cnts, dummy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5000:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        # draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.35, (0, 0, 255), 1)

        if args.upload:
            if text == "Occupied":
                if (timestamp - lastUploaded).seconds >= 3:
                    motionCounter += 1

                    if motionCounter >= 8:
                        t = tempimg.TempImage()
                        cv2.imwrite(t.path, frame)

                        print("[UPLOAD] {}".format(ts))
                        # path = "{base_path}/{timestamp}.jpg".format(
                        #        base_path="", timestamp=ts)
                        file_name = "PiCam {}".format(ts)
                        gdrive.upload_to_drive(t.path, file_name)
                        t.cleanup()

                        lastUploaded = timestamp
                        motionCounter = 0

        if args.live:
            cv2.imshow("Feed", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            rawCapture.truncate(0)

if __name__ == '__main__':
    main()
