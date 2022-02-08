    ****************************************
    * Microbot TeachMover Control Software *
    ****************************************

    This software allows for the control of a TeachMover robotic arm via serial connection. 
    The class contained in teachmover.py can be imported into other programs and used for control.
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
