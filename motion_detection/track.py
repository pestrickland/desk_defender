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
import logging.config
import yaml
import os


class Tracker():
    """A motion tracker object."""

    def __init__(self, conf, logger=None):
        """Initialise video stream.

        Arguments:
            conf (dict): Configuration settings.
        """
        super(Tracker, self).__init__()
        self.conf = conf
        self.camera_warmup_time = conf["camera_warmup_time"]
        self.framerate = conf["framerate"]
        self.min_area = conf["min_area"]
        self.min_motion_frames = conf["min_motion_frames"]
        self.min_upload_seconds = conf["min_upload_seconds"]
        self.resolution = tuple(conf["resolution"])
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("""
Initialised with these settings:
    Resolution: {}
    Framerate: {}
    Detection area: {}""".format(self.resolution,
                                 self.framerate,
                                 self.min_area))
        self.logger.info("Warming up")
        self.stopped = False
        self.stream = VideoStream(usePiCamera=conf["picamera"],
                                  framerate=self.framerate,
                                  resolution=self.resolution).start()
        time.sleep(self.camera_warmup_time)
        self.last_uploaded = datetime.datetime.now()
        self.motion_counter = 0

    def simple_detect(self, image_width=500, delta_thresh=5,
                      iterations=2):
        """Detect motion using averaged background subtraction.

        Arguments:
            image_width (int): The width used to resize the captured image.
            delta_thresh (int): The threshold for detection.
            iterations (int): The number of iterations used to dilate the
                thresholded image.

        Returns:
            coordinates (tuple): The coordinates of detected object's centroid.

        """
        average = None
        while True:
            try:
                # Grab a frame and resize it.
                self.frame = self.stream.read()
                self.frame = imutils.resize(self.frame, width=image_width)
                timestamp = datetime.datetime.now()
                text = "No motion detected."

                # Convert frame to greyscale and apply blur.
                grey = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                grey = cv2.GaussianBlur(grey, (21, 21), 0)
                if average is None:
                    self.logger.info("Starting background model")
                    average = grey.copy().astype("float")
                    continue
                cv2.accumulateWeighted(grey, average, 0.5)
                frame_delta = cv2.absdiff(grey, cv2.convertScaleAbs(average))
                # Threshold the delta image, dilate the thresholded image to
                # fill in holes and then find contours on the thresholded
                # image.
                threshold = cv2.threshold(frame_delta, delta_thresh, 255,
                                          cv2.THRESH_BINARY)[1]
                threshold = cv2.dilate(threshold, None, iterations)
                (dm, contours, dm) = cv2.findContours(threshold.copy(),
                                                      cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_SIMPLE)

                # Loop over each contour.
                if contours:
                    self.logger.debug("{} contour(s) detected.".format(
                                      len(contours)))
                for i, c in enumerate(contours):
                    # If the contour is too small, ignore it.
                    if cv2.contourArea(c) < self.min_area:
                        self.logger.debug("Contour {} rejected.".format(i + 1))
                        continue

                    # Compute the bounding box for the contour, draw it on the
                    # frame and update the text.
                    (x, y, w, h) = cv2.boundingRect(c)
                    self.logger.debug("Contour {}:\n"
                                      "{} w, {} h".format(i, w, h))
                    cv2.rectangle(self.frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

                    # Calculate contour centroid.
                    moments = cv2.moments(c)
                    cx = int(moments["m10"] / moments["m00"])
                    cy = int(moments["m01"] / moments["m00"])
                    self.logger.debug("Centroid coordinates: {}, {}".format(
                                      cx, cy))

                    text = "Motion detected."
                    self.logger.info(text)
                    # Draw circle on contour centroid.
                    cv2.circle(self.frame, (cx, cy), 10, (0, 0, 255))

                # Draw the text and timestamp on the frame.
                ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
                cv2.putText(self.frame, "Status: {}".format(text), (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(self.frame, ts, (10, self.frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                if self.conf["upload"]:
                    if text == "Motion detected.":
                        if ((timestamp - self.last_uploaded).seconds >=
                                self.min_upload_seconds):

                            self.motion_counter += 1

                            if self.motion_counter >= self.min_motion_frames:
                                t = tempimg.TempImage()
                                cv2.imwrite(t.path, self.frame)

                                print("[UPLOAD] {}".format(ts))
                                file_name = "PiCam {}".format(ts)
                                gdrive.upload_to_drive(t.path, file_name)
                                t.cleanup()

                                self.last_uploaded = timestamp
                                self.motion_counter = 0

                if self.conf["show_video"]:
                    cv2.imshow("Frame", self.frame)
                    key = cv2.waitKey(50) & 0xFF

                    if key == ord("q"):
                        self.logger.debug("q key pressed.")
                        self.stream.stop()
                        break
            except KeyboardInterrupt:
                self.logger.info("CTRL+C received, exiting")
                try:
                    # Delete image if upload not complete.
                    t.cleanup()
                except:
                    pass
                break


def setup_logging(default_path="logging.yaml", default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """Set up logging configuration."""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main():
    """Capture video from Raspberry Pi camera and detect movement."""
    parser = argparse.ArgumentParser("Configure image tracker.",
                                     parents=[gdrive.flags])
    parser.add_argument("-u", "--upload", help="upload images to Google Drive",
                        action="store_true")
    parser.add_argument("-l", "--live", help="show live output",
                        action="store_true")
    parser.add_argument("-c", "--conf", required=True,
                        help="Path to the JSON configuration file.")
    parser.add_argument("-v", "--verbose", help="Increase verbosity",
                        action="count")
    args = parser.parse_args()
    with open(args.conf) as f:
        conf = yaml.safe_load(f.read())

    # Overwrite config file with commandline arguments.
    if args.live:
        conf["show_video"] = True
    if args.upload:
        conf["upload"] = True

    # Configure logging.
    setup_logging()
    logger = logging.getLogger("Tracker")
    if args.verbose is not None:
        logger.setLevel(logging.DEBUG)

    tracker = Tracker(conf, logger=logger)
    tracker.simple_detect(image_width=500,
                          delta_thresh=conf["delta_thresh"],
                          iterations=2)

if __name__ == '__main__':
    main()
