from collections import deque
import os
import numpy as np


class Stick:
    def __init__(self, name):
            self.points = deque(maxlen=4)
            self.minPoint = 500
            self.isGoingDown = False
            self.min = 500
            self.name = name

    def getName(self,name):
        return self.name

    def setMin(self, min):
        self.min = min

    def getMin(self):
        return self.min

    def getIsGoingDown(self):
        return self.isGoingDown

    def updateIsGoingDown(self, isGoingDown):
        self.isGoingDown = isGoingDown

    def getPoints(self):
        return self.points

    def addPoint(self, x, y):
        self.points.appendleft((x, y))

    def getX(self):
        return self.points[0][0]

    def getY(self):
        return self.points[0][1]

import simpleaudio as sa

class DrumSound:
    def __init__(self, name, ):
        self.name = name
        self.sounds = []
        self.load()
    def load(self):
        for i in range(1, 6):
            path = r'C:\Users\aadi1\PycharmProjects\pythonProjecttriall chris\audio\\' + self.name + '\\' + self.name + str(
                i) + ".wav"
            sound = sa.WaveObject.from_wave_file(path)
            self.sounds.append(sound)

    def play(self, volumeIndex):
        if volumeIndex < 0:
            self.sounds[0].play()
        elif volumeIndex >= 5:
            self.sounds[4].play()
        else:
            self.sounds[volumeIndex].play()

from threading import Thread
import cv2

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

from imutils.video import FileVideoStream
from imutils.video import FPS
import argparse
import cv2
import imutils
import time

# Create instances of the DrumSound class
snare = DrumSound("Snare")
kick = DrumSound("Kick")
tom = DrumSound("Tom")
floor = DrumSound("Floor")
hihat = DrumSound("Hat")
ride = DrumSound("Ride")


def trackStick(stick):
    stick.setMin(min(stick.getMin(), stick.getY()))
    if (len(stick.getPoints()) == 4):
        yDirection = stick.getPoints()[3][1] - stick.getPoints()[0][1]
        if (stick.getIsGoingDown() and yDirection < -20):
            volume = 600 - stick.getMin()
            volume = int(volume / 100) - 1
            # snare.play(volume)
            playDrumByPosition(stick.getX(), stick.getY(), volume)
            stick.setMin(600)
            stick.updateIsGoingDown(False)
        if np.abs(yDirection) > 20 and yDirection >= 0:
            stick.updateIsGoingDown(True)
    return


def playDrumByPosition(x, y, volume):
    if (x < 150):
        kick.play(volume)
    elif (x < 450):
        snare.play(volume)
    else:
        hihat.play(volume)


def main():
    center = deque(maxlen=2)
    center.appendleft((0, 0))
    center.appendleft((0, 0))
    leftStick = Stick("left")
    rightStick = Stick("right")
    # Upper and lower bounds (HSV) for the stick color
    objLower = (30, 86, 14)
    objUpper = (97, 244, 255)
    frameCount = 0
    vs = WebcamVideoStream(src=0).start()

    # vs = FileVideoStream(0).start()
    time.sleep(1.0)
    while True:
        # Read in 1 frame at a time and flip the image
        frame = vs.read()

        # frame = imutils.resize(frame, width = 600, height = 300)
        frame = cv2.flip(frame, 1)
        overlay = frame.copy()
        alpha = 0.5
        cv2.line(overlay, (150, 0), (150, 600), (138, 138, 138), 1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.line(frame, (450, 0), (450, 600), (138, 138, 138), 1)

        # Mask the image so the result is just the drum stick tips
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, objLower, objUpper)
        mask = cv2.erode(mask, None, iterations=1)

        # Find contours in the mask
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # sort cnts so we can loop through the two biggest (the sticks hopefully)
        cnts = sorted(cnts, key=lambda x: cv2.contourArea(x), reverse=True)

        numSticks = min(len(cnts), 2)
        for i in range(numSticks):
            ((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
            if (radius > 4):
                center.appendleft((int(x), int(y)))
        for i in range(numSticks):
            if (numSticks > 1):
                if (center[i][0] <= center[(i + 1) % 2][0]):
                    cv2.circle(frame, center[i], 10, (156, 76, 76), 3)
                    leftStick.addPoint(center[i][0], center[i][1])
                    if (frameCount > 4):
                        trackStick(leftStick)
                else:
                    cv2.circle(frame, center[i], 10, (76, 76, 156), 3)
                    rightStick.addPoint(center[i][0], center[i][1])
                    if (frameCount > 4):
                        trackStick(rightStick)
            # Only one stick - split screen in half
            else:
                if (center[i][0] >= 300):
                    leftStick.addPoint(center[i][0], center[i][1])
                    if (frameCount > 4):
                        trackStick(leftStick)
                else:
                    rightStick.addPoint(center[i][0], center[i][1])
                    if (frameCount > 4):
                        trackStick(rightStick)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        frameCount += 1

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    vs.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()