"""`track` uses background subtraction to detect moving targets."""
import cv2
import time
import argparse
import datetime
import imutils
from imutils.video import VideoStream
import gdrive
import tempimg
import logging
from picamera import PiCamera
from picamera.array import PiRGBArray


class Camera():
	"""A camera object."""
	
	def __init__(self, args):
		self.args = args
		self.stopped = False

	def start(self):

		stream = VideoStream(usePiCamera=args["picamera"] > 0).start()
		time.sleep(2)

		while True:
			# Grab a frame and resize it.
			frame = stream.read()
			frame = imutils.resize(frame, width=400)

			if self.stopped == True:
				break

			

			if key == ord("q"):
				self.stopped = True	


class Tracker():
    """A motion tracker object."""

    def __init__(self, conf):
        super(Tracker, self).__init__()
        self.conf = conf
        self.resolution = tuple(conf["resolution"])
        self.framerate = conf["framerate"]
        self.min_area = conf["min_area"]
        camera = PiCamera()
        camera.resolution = self.resolution
        camera.framerate = self.framerate
        self.camera = camera

        last_uploaded = datetime.datetime.now()
        motion_counter = 0

    def simple_detect(self, image_width=500, delta_thresh=5, iterations=2):
        """Detect motion using averaged background subtraction.

        Arguments:
            image_width (int): The width used to resize the captured image.
            delta_thresh (int): The threshold for detection.
            iterations (int): The number of iterations used to dilate the
                thresholded image.

        Returns:
            coordinates (tuple): The coordinates of detected object's centroid.

        """
        # TODO: Abstract the camera set-up from the act of reading each frame.
        #       Consider a camera class with start, read, stop methods, for use
        #       by the detection `while` loop.
        average = None

        for f in self.camera.capture_continuous(self.raw_capture,
                                                format="bgr",
                                                use_video_port=True):
            frame = f.array
            timestamp = datetime.datetime.now()
            text = "No motion detected"
            frame = imutils.resize(frame, width=image_width)
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            grey = cv2.GaussianBlur(grey, (21, 21), 0)
            if average is None:
                logging.info("Starting background model")
                average = grey.copy().astype("float")
                self.raw_capture.truncate(0)
                continue
            cv2.accumulateWeighted(grey, average, 0.5)
            frame_delta = cv2.absdiff(grey, cv2.convertScaleAbs(average))
            # Threshold the delta image, dilate the thresholded image to fill
            # in holes and then find contours on the thresholded image.
            threshold = cv2.threshold(frame_delta, delta_thresh, 255,
                                      cv2.THRESH_BINARY)[1]
            threshold = cv2.dilate(threshold, None, iterations)
            (dm, contours, dm) = cv2.findContours(threshold.copy(),
                                                  cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)

            # Loop over each contour.
            for c in contours:
                # If the contour is too small, ignore it.
                if cv2.contourArea(c) < self.min_area:
                    continue

                # Compute the bounding box for the contour, draw it on the
                # frame and update the text.
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Motion detected."
                logging.info(text)

                moments = cv2.moments(c)
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])

                # Draw circle on contour centroid.
                cv2.circle(frame, (cx, cy), 10, (0, 0, 255))

                logging.info("Coordinates: {}, {}".format(cx, cy))

            # Draw the text and timestamp on the frame.
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, "Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


def main():
    """Capture video from Raspberry Pi camera and detect movement."""
    parser = argparse.ArgumentParser("Configure image tracker.",
                                     parents=[gdrive.FLAGS])
    parser.add_argument("-u", "--upload", help="upload images to Google Drive",
                        action="store_true")
    parser.add_argument("-l", "--live", help="show live output",
                        action="store_true")
    args = parser.parse_args()

    camera = Camera(args)


    if args.upload:
        if text == "Occupied":
            if (timestamp - lastUploaded).seconds >= 3:
                motionCounter += 1

                if motionCounter >= 8:
                    t = tempimg.TempImage()
                    cv2.imwrite(t.path, frame)

                    print("[UPLOAD] {}".format(ts))
                    file_name = "PiCam {}".format(ts)
                    gdrive.upload_to_drive(t.path, file_name)
                    t.cleanup()

                    lastUploaded = timestamp
                    motionCounter = 0

    if args.live:
        cv2.imshow("Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            camera.stop()
        rawCapture.truncate(0)

if __name__ == '__main__':
    main()
