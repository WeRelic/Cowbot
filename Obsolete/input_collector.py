"""
    input_collector.py
    
    Record and translate controller inputs into a valid format for RLBot.

    TODO:
        - Frame interpolation:
            Currently, if a frame finds that there is acceleration in one frame,
            it doesn't carry over to the next (or until there is deceleration).

            This applies to "Boost" and "Brake" as well.

"""

from inputs import get_gamepad
from enum import Enum
from threading import Thread, Lock
from time import sleep
from FrameInput import *



# Set for 120 FPS resolution
frame_timelimit = 0.0083333333333


ms_time = lambda: int( round( time.time() * 1000 ) )
bindings = {
        "Throttle" : "RT",
        "Steer"    : "LSX",
        "Pitch"    : "LSY",
        "Yaw"      : "LSX",
        "Roll"     : "LB",
        "Boost"    : "RB",
        "Brake"    : "LB",
        "Jump"     : "X",
        "Accel"    : "RT",
        "Decel"    : "LT"
    }



def input_listener_thread( flag, eventlist ):
    local_binds = {
        "ABS_Y"     : "LSY",        # Left stick up/down
        "ABS_X"     : "LSX",        # Left stick left/right
        "BTN_TL"    : "LB",         # Left bumper
        "BTN_TR"    : "RB",         # Right bumper
        "ABS_Z"     : "LT",         # Left trigger
        "ABS_RZ"    : "RT",         # Right trigger
        "BTN_WEST"  : "X"           # X Button
    }
    while not flag.acquire(False):
        events = get_gamepad()
        for event in events:
            if event.code in local_binds.keys():
                print( "\t\tEvent: {}".format( local_binds[event.code] ) )
                eventlist.append(
                    InputEvent(
                        local_binds[event.code],
                        event.timestamp,
                        event.state
                    ) )







class InputEvent:
    def __init__( self, code, timestamp, state = None ):
        self.code = code
        self.timestamp = timestamp
        self.state = state

    def is_earlier_than( self, other ):
        return self.timestamp < other.timestamp

    def is_same_code( self, other ):
        return self.code == other.code

    def is_same_state( self, other ):
        return self.state == other.state

    def __str__( self ):
        return "Code: {0.code}, Time: {0.timestamp}, State: {0.state}".format( self )

    def __lt__( self, other ):
        return self.timestamp < other.timestamp
    

class SequenceFrame:
    def __init__( self, frameid, input_list = [] ):
        self.inputlist = input_list
        self.frameid   = frameid

    def __str__( self ):
        framedata = ""
        for inp in self.inputlist:
            framedata = "{}\n\t\t{}".format( framedata, inp )
        return "SeqFrame:\n\tOffset:{}\n\tInputs:{}".format( self.frameid, framedata )

    def get_latest_event( self, code ):
        latest = 0.0
        ev = None
        for event in self.inputlist:
            if event.code == code:
                if event.timestamp >= latest:
                    latest = event.timestamp
                    ev = event
        return event

    def get_valid_time( self ):
        return self.inputlist[-1].timestamp

    def to_FrameInput( self ):
        # Getting the latest event of each binding.
        latest = {}
        for k, v  in bindings.items():
            latest_ts = 0.0
            ev = None
            for event in self.inputlist:
                if event.code == v:
                    if event.timestamp >= latest_ts:
                        latest_ts = event.timestamp
                        ev = event
            latest[k] = ev

        for k,v in latest.items():
            
            if k in [ "Throttle", "Steer", "Pitch",
                      "Yaw", "Roll", "Accel", "Decel" ] and v == None:
                latest[k] = InputEvent( k, self.get_valid_time(), 0.0 )
            elif k in [ "Brake", "Boost", "Jump" ] and v == None:
                latest[k] = InputEvent( k, self.get_valid_time(), 0 )
                
            print( "{}:\n\t{}".format( k, v ) )

        # Accounting for throttle being controlled by two buttons:
        latest["Throttle"].state = latest["Accel"].state - latest["Decel"].state
        # Editing value states to comform with RLBot's interface:
        # Love me some magic numbers... Sorry.
        return FrameInput(
            self.frameid,
            latest["Throttle"].state / 255.0,
            latest["Steer"].state / 32767.0,
            latest["Pitch"].state / 32767.0,
            latest["Yaw"].state / 32767.0,
            latest["Roll"].state / 32767.0,
            latest["Jump"].state,
            latest["Boost"].state,
            latest["Brake"].state,
            )
        
    
    def add_input( self, inp = None ):
        self.inputlist.append( inp )

    


class InputListener:
    def __init__( self ):
        self.events = []
        self.frames = []
        self.listening = Lock()
        self.worker = Thread(
            target = input_listener_thread,
            name = "Listener Thread",
            args = ( self.listening, self.events )
        )
        self.interp_states = {
            "boost" : False,
            "brake" : False,
            "jump"  : False
        }
        

    def within_frame( self, timestamp, frametime, frametime_limit ):
        upper_bound = frametime + frametime_limit
        return timestamp >= frametime and timestamp <= upper_bound
        
    

    def generate_frames( self ):
        """
            Iterates event list and generates a list of SequenceFrame objects.
            Returns the number of frames generated.
        """
        print( "Sorting events by timestamp..." )
        # Get earliest and latest events
        e = sorted( self.events, key = lambda x : x.timestamp )

        print( "Found earliest and latest events..." )
        early, late = e[0].timestamp, e[-1].timestamp
        framelist = []
        frametime = early
        while frametime <= late:
            # Append any event in the valid time range for this frame.
            print( "\tFinding events between {} and {}".format( frametime, frametime + frame_timelimit ) )
            framelist.append(
                [ x for x in e if self.within_frame( x.timestamp, frametime, frame_timelimit ) ]
            )
            frametime += frame_timelimit

        # Generating Sequence Frame Objects...
        print( "Generating Sequence Frame Objects..." )
        frameid = 0
        for frame in framelist:
            print( "Generating SequenceFrame with offset of {}:".format( frameid ) )
            if len( frame ) > 0:
                if ( 
                print( "\tGenerated frame with {} inputs...".format( len( frame ) ) )
                self.frames.append( SequenceFrame( frameid, frame ) )
                
            else:
                print( "\tGenerated empty frame..." )
            frameid += 1
        return len( framelist )



    def begin_listening( self ):
        print( "Listening for controller inputs..." )
        self.listening.acquire()
        self.worker.start()

    def cease_listening( self ):
        print( "No longer listening for controller inputs; Joining listener thread..." )
        self.listening.release()
        self.worker.join()
        print( "Generating frames..." ) 
        self.generate_frames()
        
                    
if __name__ == "__main__":
    listener = InputListener()
    listener.begin_listening()
    sleep( 5 )
    listener.cease_listening()
    for frame in listener.frames:
        print( frame.to_FrameInput() )
    
        