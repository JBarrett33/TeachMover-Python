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

class TeachMover():

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
    def __send_cmd(self, cmd: str) -> str:

    #First, send the command.

        if not cmd.endswith("\r"):
            cmd += "\r"

        self.con.write(cmd.encode())

    #Then, read and return the response!
        response = ""
        while self.con.in_waiting == 0:
            #Do nothing until a response is recieved
            continue

        for i in range(0, self.con.in_waiting):
            incomingByte = self.con.read()
            response += incomingByte.decode()
            response = response.rstrip()
        return response


