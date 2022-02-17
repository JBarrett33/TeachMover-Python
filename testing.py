from teachmover import TeachMover
import time

winston = TeachMover("COM3", 9600)

winston.moveAngle(200, 0, 30, 30)
time.sleep(2)
winston.returnToZero()

