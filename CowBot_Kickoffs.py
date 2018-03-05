"""

    CowBot_Kickoffs.py

    This script defines the various hardcoded kickoff sequences.

    Have fun, Lie!    
"""

from CowBotControlSequence import *
from FrameInput import *

## Left Side Diagonal Kickoffs:

DIAG_KICKOFF_L = ControlSequence( "Left Diagonal Kickoff", [
        FrameInput() # Hardcode inputs here.
    ] )

DIAG_KICKOFF_L_FAST = ControlSequence( "Fast Left Diagonal Kickoff", [
        FrameInput()
    ] )
    

    
    
## Right Side Diagonal Kickoffs:

DIAG_KICKOFF_R = ControlSequence( "Right Diagonal Kickoff", [
        FrameInput() # Hardcode inputs here.
    ] )

DIAG_KICKOFF_R_FAST = ControlSequence( "Fast Right Diagonal Kickoff", [
        FrameInput() 
    ] )

    
    
## Left Side Kickoffs:

SIDE_KICKOFF_L = ControlSequence( "Left Side Kickoff", [
        FrameInput() # Hardcode inputs here.
    ] )


    
    
## Right Side Kickoffs:
SIDE_KICKOFF_R = ControlSequence( "Right Side Kickoff", [
        FrameInput() # Hardcode inputs here.
    ] )

    
    

## Direct Kickoffs
    
GOAL_KICKOFF   = ControlSequence( "Goalie Position Kickoff", [
        FrameInput() # Hardcode inputs here.
    ] )
