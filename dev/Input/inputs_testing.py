"""Simple example showing how to get gamepad events."""

from __future__ import print_function


from inputs import get_gamepad

"""
Codes:
    BTN_TL = L Bumper
    BTN_TR = R Bumper
    
"""

ms_time = lambda: int(round(time.time() * 1000))


if __name__ == "__main__":
    inputlist = []
    while 1:
        events = get_gamepad()
        for event in events:
            # Ignoring sync report events.
            if event.ev_type == "Sync":
                pass

            # Ignoring dpad presses. 
            elif event.code == "ABS_HAT0X":
                pass


            # TODO: Output stick movement values. 
            elif event.code in [ "ABS_Y", "ABS_X" ]:
                print( "Left Stick Moved @ {}".format( event.timestamp ) )
                
            elif event.code in [ "ABS_RX", "ABS_RY" ]:
                print( "Right Stick Moved @ {}".format( event.timestamp ) )


            # TODO: Output trigger state.                 
            elif event.code == "ABS_Z":
                print( "Left Trigger Pulled" )
                
            elif event.code == "ABS_RZ":
                print( "Right Trigger Pulled" )





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
                print(event.ev_type, event.code, event.state)
        
