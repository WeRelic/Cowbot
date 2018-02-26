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
        self.generated   = False

    def Generate( self, starting_frame ):
        """
            Generate the required frame inputs using the given script.

            Hardcoded inputs will be put into the input queue.
        """
        if !self.generated:
            self.inputs = self.hardcoded
            for x in self.inputs:
                x.frameid = x.frameid + starting_frame
            if self.script != None:
                result = self.script( starting_frame )
                while result != None:
                    self.inputs.append( result )
                    result = self.script( starting_frame )
            self.generated = True
        

    def GetFrame( self ):
        try:
            return self.inputs.pop(0)
        except IndexError:
            return None
        

    def Run( self, starting_frame ):
        print( "Running subroutine: {}".format( self.name ) )
        Generate( starting_frame )
        while True:
            result = self.GetFrame()
            if result != None:
                yield result
            else:
                break
        self.inputs = []
        self.generated = False
        yield None
        

