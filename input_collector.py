"""Simple example showing how to get gamepad events."""

from inputs import get_gamepad
from FrameInput import *
from enum import Enum

"""
Codes:
    BTN_TL = L Bumper
    BTN_TR = R Bumper
    
"""

ms_time = lambda: int( round( time.time() * 1000 ) )

class InputEvent:
    def __init__( self, code, timestamp, state = None ):
        self.code = code
        self.timestamp = timestamp
        self.state = state

    def is_earlier_than( self, other ):
        

class SequenceFrame:
    bindings = {
            "Throttle" : "RTRIGGER",
            "Steer"    : "LSTICK_X",
            "Pitch"    : "

        }
    
    def __init__( self, frameid, input_list = [] ):
        self.inputlist = input_list
        self.frameid   = frameid

    def parse_throttle( self, value = 0 ):
        throttle_events = [  ]
        
    
    
    def add_input( self, inp = None ):
        self.inputlist.append( inp )


    def clean( self ):
        x = 0

        while x < len( self.inputlist ):
            # Remove NULL inputs:
            if self.inputlist[ x ] == None:
                self.inputlist.pop( x )

            # Retain the latest input of the following controls:
            # Steer:
            
            
            x += 1
            
    def rlbot_interface( self ):
        """
            Convert this SequenceFrame into an FrameInput.
        """
        frame = FrameInput(
                self.frameid,
                
            )
        return frame




class InputSequence:
    def __init__( self, framelist = [] ):
        self.framelist = framelist



    def add_frame( self, inp = SequenceFrame() ):
        if len( frame.inputlist ) > 0:
            self.inputlist.append( inp )

    


if __name__ == "__main__":
    inputlist = []
    while 1:
        events = get_gamepad()
        for event in events:
            # Ignoring sync report events.
            if event.ev_type == "Sync":
                pass

            # Ignoring irrelevant input codes:
            elif event.code in [ "ABS_RX", "ABS_RY", "BTN_START", "BTN_SELECT", "ABS_HAT0X" ]:
                pass




            # Handling the Left joystick:
            elif event.code in [ "ABS_Y", "ABS_X" ]:
                if event.code == "ABS_Y":
                    print( "LSTICK_Y@{}={}".format( event.timestamp, event.state ) )
                elif event.code == "ABS_X":
                    print( "LSTICK_X@{}={}".format( event.timestamp, event.state ) )
                    
            


            # Handling the Left and Right Triggers:                
            elif event.code == "ABS_Z":
                print( "LTRIGGER@{}={}".format( event.timestamp, event.state ) )
            elif event.code == "ABS_RZ":
                print( "RTRIGGER@{}={}".format( event.timestamp, event.state ) )



            # Handling the Left Bumper:
            elif event.code == "BTN_TL" and event.state == 1:
                print( "LB_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_TL" and event.state == 0:
                print( "LB_UP@{}".format( event.timestamp ) )

            # Handling the Right Bumper:
            elif event.code == "BTN_TR" and event.state == 1:
                print( "RB_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_TR" and event.state == 0:
                print( "RB_UP@{}".format( event.timestamp ) )
                          
                

            # Handling the "Y" Button:
            elif event.code == "BTN_NORTH" and event.state == 1:
                print( "Y_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_NORTH" and event.state == 0:
                print( "Y_UP@{}".format( event.timestamp ) )
                
            
            # Handling the "B" Button:
            elif event.code == "BTN_EAST" and event.state == 1:
                print( "B_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_EAST" and event.state == 0:
                print( "B_DOWN@{}".formaT( event.timestamp ) )
                

            # Handling the "A" Button:
            elif event.code == "BTN_SOUTH" and event.state == 1:
                print( "A_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_SOUTH" and event.state == 0:
                print( "A_UP@{}".format( event.timestamp ) )


            # Handling the "X" Button:
            elif event.code == "BTN_WEST" and event.state == 1:
                print( "X_DOWN@{}".format( event.timestamp ) )
            elif event.code == "BTN_WEST" and event.state == 0:
                print( "X_UP@{}".format( event.timestamp ) )

                
            
            else:
                print( event.ev_type, event.code, event.state )
        
