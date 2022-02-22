''' 
****************************************
* Microbot TeachMover Control Software *
****************************************

This software allows for the control of a TeachMover robotic arm via serial connection. 
Ideally, this class should be imported into other programs and used solely for control.
The bot has a total of ten built-in serial commands, 8 of which will be implemented:

    @STEP       Move all steppers synchronously
    @CLOSE      Close the gripper, not much force
    @SET        Activate handheld teach control
    @RESET      Reset internal position registers / motor current shutoff
    @READ       Read values stored in internal position registers
    @QDUMP      Dump the program currently stored in memory.
    @QWRITE     Reupload a perviously dumped program.
    @RUN        Run the program currently stored in memory.

    The below commands are not implemented, mainly because there's not much
    use for them if this software is being used. 

    @ARM        Change response character from default "@"
    @DELAY      Insert a delay between TX chars.

    Potential functions to add in the future:
    HOME        home the arm (using internal position register values)
    GRIP        grip an object + 32 steps to add ~1 lb of force
    MEASURE     measure an object using the gripper

    I'd like to be able to move the bot via x, y, z coordinates as well but this could prove challenging. 
    This is more of a long-term goal. 
'''

import serial
import time
import numpy as np


class TeachMover:

    #Init function
    def __init__(self, portID: str, baudRate = 9600):
        try:
            '''
                TEACHMOVER DEFAULT SERIAL CONFIGURATION
                Baud rate:      9600bps
                Word length:    8 bits
                Start bits:     1
                Stop bits:      1
                Pairity bits:   None
                Duplexing:      Full duplex
            '''
            self.con = serial.Serial(portID, baudRate)      

        #Motor 1 (Base)
            self.motor1 = {
                "steps_rev":7072,
                "steps_rad":1125,
                "steps_deg":19.64
            }
            #Motor 2 (Shoulder)
            self.motor2 = {
                "steps_rev":7072,
                "steps_rad":1125,
                "steps_deg":19.64
            }
            #Motor 3 (Elbow)
            self.motor3 = {
                "steps_rev":4158,
                "steps_rad":661.2,
                "steps_deg":11.55
            }
            #Motor 4 (Right Wrist)
            self.motor4 = {
                "steps_rev":1536,
                "steps_rad":241,
                "steps_deg":4.27
            }
            #Motor 5 (Left Wrist)
            self.motor5 = {
                "steps_rev":1536,
                "steps_rad":241,
                "steps_deg":4.27
            } 

        except Exception as e:
            print(e)

    #Private function to send a single command to the robot via serial.
    def __sendCmd(self, cmd: str, waitTime = 0.5) -> str:

    #Send the command.
        if not cmd.endswith("\r"):
            cmd += "\r"
        self.con.write(cmd.encode())

    #Read/return the response as a float array for future expansion
        while self.con.in_waiting == 0:
            continue
        time.sleep(waitTime)

        tmp = ""

        for i in range(0, self.con.in_waiting):
            tmp += self.con.read().decode()
        tmp = tmp.replace(" ", ",")
        tmp = tmp.replace("\r", ",")
        tmp = tmp.split(",")
        tmp = tmp[:-1]

        ret = []

        for i in tmp:
            ret.append(int(i))

        return ret

    def setZero(self) -> int:
        return self.__sendCmd("@RESET")[0]
   
    def moveSteps(self, speed = 0, base = 0, shoulder = 0, elbow = 0, pitch = 0, roll = 0, gripper = 0, output = -1):
        if output == -1:
            return self.__sendCmd(f"@STEP {speed}, {base}, {shoulder}, {elbow}, {pitch - roll}, {pitch + roll}, {gripper + elbow}")[0]
        else:
            return self.__sendCmd(f"@STEP {speed}, {base}, {shoulder}, {elbow}, {pitch - roll}, {pitch + roll}, {gripper + elbow}, {output}")[0]

    def moveAngle(self, speed = 0, base_deg = 0, shoulder_deg = 0, elbow_deg = 0, pitch_deg = 0, roll_deg = 0):

        b = int(base_deg * self.motor1["steps_deg"])
        s = int(shoulder_deg * self.motor2["steps_deg"])
        e = int(elbow_deg * self.motor3["steps_deg"])
        p = int(pitch_deg * self.motor4["steps_deg"])
        r = int(roll_deg * self.motor5["steps_deg"])

        return self.moveSteps(speed, b, s, e, p, r)

    def readPosition(self) -> list:
        return self.__sendCmd("@READ")[1:-1]

    def readInputs(self) -> int:
        temp = self.__sendCmd("@READ")
        inputByte = temp[7] % 256
        return inputByte

    def lastKey(self)->str:
        keymap = {0:"None", 1:"Train", 2:"Pause", 3:"Grip",
            4:"Out", 5:"Free", 6:"Move", 7:"Stop",
            8:"Step", 9:"Point", 10:"Jump", 11:"Clear",
            12:"Zero", 13:"Speed", 14:"Run"}
        temp = self.__sendCmd("@READ")
        subt = temp[7] % 256
        lastKey = (temp[7] - subt) / 256
        return keymap[lastKey]

    def closeGripper(self) -> int:
        return self.__sendCmd("@CLOSE")[0]

    def gripObject(self) -> int:
        self.closeGripper()
        return self.__sendCmd("@STEP 220, 0, 0, 0, 0, 0, -32")

    def releaseObject(self) -> int:
        return self.__sendCmd("@STEP 220, 0, 0, 0, 0, 0, 500")

    def returnToZero(self) -> int:
        currentPos = self.readPosition()

        speed = 220
        base = int(-currentPos[0])
        shoulder = int(-currentPos[1])
        elbow = int(-currentPos[2])
        wrist1 = int(-currentPos[3])
        wrist2 = int(-currentPos[4])
        grip = int(-currentPos[5])
        ret = self.__sendCmd(f"@STEP {speed}, {base}, {shoulder}, {elbow}, {wrist1}, {wrist2}, {grip}")
        #We can execute setZero to cut current to the motors. 
        self.setZero()
        return ret

    def measureObject(self) -> float:
        OFFSET = 0
        self.closeGripper()
        current_width_mm = (self.readPosition()[5] / 14.6) - OFFSET
        return current_width_mm

    #Simply execute the @QDUMP command and strip the status code. Processing will actually be handled elsewhere. 
    def dumpRAM(self) -> list:
        res = self.__sendCmd("@QDUMP", 3)[1:]
        return res

    def saveProgram(self, filePath: str):
        data = self.dumpRAM()
        with open(filePath, 'w+') as file:
            counter = 1
            for i in data:
                if counter % 8 == 0:
                    file.write(str(i))
                    file.write("\r")
                else:
                    file.write(f"{str(i)},")
                counter = counter + 1

    def loadProgram(self, filePath: str):
        with open(filePath, 'r') as file:
            lineCount = 0
            for line in file:
                print(line)
                if not line.isspace():
                    self.__sendCmd(f"@QWRITE {line}")
            
    #Work in progress: Inverse kinematic functions

    def moveToCoordinates(self, x, y, z, p, r, r1):
        H = 195.0
        L = 177.8
        LL = 96.5
        p = np.radians(p)
        r = np.radians(r)

        #T1 Calculations
        if x == 0:
            T1 = (np.pi / 2) * np.sign(y)
        else:
            T1 = np.arctan(y / x)

        #RR, R0, Z0
        #TODO may need some work... IDK if we need np.degrees or not.
        RR = np.sqrt(x**2 + y**2)
        R0 = RR - LL * np.cos(np.degrees(p))
        Z0 = z - LL * np.sin(np.degrees(p)) - H

        if R0 == 0:
            B = np.sign(Z0) * (np.pi / 2)
        else:
            B = np.arctan(Z0 / R0)

        #A calculations
        A = R0**2 + Z0**2
        A = 4 * (L**2) / (A) - 1
        A = np.arctan(np.sqrt(A))

        #T2 - T5 Calculations
        T2 = (np.pi/2) - (A + B)
        T3 = B - A
        T4 = p - r - r1 * T1
        T5 = p + r + r1 * T1

        #Convert to steps and accomodate for offset start position

        currentPos = self.readPosition().data

        T1 = int(T1 * 1125) - int(currentPos[0])
        T2 = int(T2 * 1125) - int(currentPos[1])
        T3 = -int(T3 * 672) - int(currentPos[2])
        T4 = int(T4 * 241) - int(currentPos[3])
        T5 = int(T5 * 241) - int(currentPos[4])
        T6 = T3

        return self.moveSteps(220, T1, T2, T3, 0, 0, T6)
