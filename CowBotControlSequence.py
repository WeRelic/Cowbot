"""

    CowBot_ControlSequence.py

    In this script we'll define a ControlSequence.

    A ControlSequence acts as a superclass for HardSequence and SoftSequence.


"""

import FrameInput


class ControlSequence:
    """
        Contains a list of FrameInputs to be run at the desired times.

        If 'script' == None:
            The sequence is hardcoded to run the given inputs until inputs are exhausted.
        else:
            The sequence will generate inputs on the fly until the given script returns None.
    """
    def __init__( self, name, inputs = [], script = None ):
        self.hardcoded   = inputs
        self.inputs      = []
        self.name        = name
        self.script      = script
        self.input_index = 0

    def Generate( self, starting_frame ):
        """
            Generate the required frame inputs using the given script.

            Hardcoded inputs will be put into the input queue.
        """
        self.inputs = self.hardcoded
        if self.script != None:
            result = self.script( starting_frame )
            if result != None:
                self.inputs.append( result )


    def GetFrame( self ):
        try:
            result = self.inputs[ self.input_index ]
            self.input_index += 1
            return result
        except IndexError:
            self.input_index = 0
            return None
        

    def Run( self ):
        print( "Running subroutine: {}".format( self.name ) )
        Generate()
        while True:
            result = self.GetFrame()
            if result != None:
                yield result
            else:
                break
        return None
        

