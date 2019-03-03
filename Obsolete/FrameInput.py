"""

    This file contains the FrameInput class, which is part of the CowBot_Control package.


    TODO:
        Implement regex search for FrameInput so we can hardcode frame inputs
        e.g:
            Frame(100,1.0,0.0,0.0,0.0,0.0,1,1,0)
            means the bot jumps and boosts on frame 100)

I changed "brake" to "drift" to avoid potential confusion with negative throttle.
"""

class FrameInput:
    """
        This class represents a single frame worth of user input.
    """
    def __init__( self, 
            frameid  = 0,
            throttle = 0.0,
            steer    = 0.0,
            pitch    = 0.0,
            yaw      = 0.0,
            roll     = 0.0,
            jump     = 0,
            boost    = 0,
            drift    = 0 ):
        self.frameid  = frameid
        self.throttle = throttle
        self.steer    = steer
        self.pitch    = pitch
        self.yaw      = yaw
        self.roll     = roll
        self.jump     = jump
        self.boost    = boost
        self.drift    = drift
        
        
    def __str__( self ):
        data = "{0.frameid},{0.throttle},{0.steer},{0.pitch},{0.yaw},{0.roll},{0.jump},{0.boost},{0.drift}"
        return "Frame({})".format( data.format( self ) )


    def ToList( self ):
        """
            Return a list containing the values of the FrameInput.
            This is to interface with RLBot.py
        """
        return [
                self.throttle,
                self.steer,
                self.pitch,
                self.yaw,
                self.roll,
                self.jump,
                self.boost,
                self.drift                
            ]

    
    def FromStr( self, string ):
        """
            Extract a FrameInput value from a string and change this object's values.

            This function is brittle. A regex solution would be more robust.
        """
        data = string.split("(")[1].split(")")[0].split(",")
        
        self.frameid  = int( data[0] )
        self.throttle = float( data[1] )
        self.steer    = float( data[2] )
        self.pitch    = float( data[3] )
        self.yaw      = float( data[4] )
        self.roll     = float( data[5] )
        self.jump     = int( data[6] )
        self.boost    = int( data[7] )
        self.drift    = int( data[8] )


    @classmethod
    def FromStr( cls, string ):
        """
            Extract a FrameInput value from a string and create a new FrameInput object.

            This function is brittle. A Regex solution would be more robust.
        """
        data = string.split("(")[1].split(")")[0].split(",")

        data[0] = int( data[0] )
        data[1] = float( data[1] )
        data[2] = float( data[2] )
        data[3] = float( data[3] )
        data[4] = float( data[4] )
        data[5] = float( data[5] )
        data[6] = int( data[6] )
        data[7] = int( data[7] )
        data[8] = int( data[8] )
        
        return FrameInput( *data )
        
#I don't know what this is for
if __name__ == "__main__":
    test_object1 = FrameInput(15)
    test_object2 = FrameInput()
    
    test_string1 = str( test_object1 )
    test_string2 = str( test_object2 )
    
    classmet_parse = FrameInput.FromStr( test_string1 )
    instance_parse = FrameInput.FromStr( test_string2 )

    print( classmet_parse )
    print( instance_parse )
    
