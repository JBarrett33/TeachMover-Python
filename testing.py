from teachmover import TeachMover
import time

winston = TeachMover("COM3", 9600)


winston.moveSteps(220, 800, 300, 500, 122, 60)
winston.returnToZero()
