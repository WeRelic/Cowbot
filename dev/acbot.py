from math import pi, cos, sin, atan2, sqrt
from CowBotVec2 import Vector2
import CowBotControlSequence


URotationToRadians = pi / 32768.0

# A control sequence allows a subroutine to take over planning for the agent
# for a number of frames. This is useful for things like half-flipping, etc.
class ControlSequence:
    def __init__( self, num_frames, f ):
        self.num_frames = num_frames
        self.f = f
        
    def get_output_vector(self):
        if (self.num_frames == 0):
            return None
        else:
            result = self.f(self.num_frames)
            self.num_frames -= 1
            return result


    

class Agent:
    
    # This is the boosts in order
    boost_pills = [
        Vector2(  61.5 * 50,  82 * 50 ),
        Vector2( -61.5 * 50,  82 * 50 ), 
        Vector2( -71.5 * 50,   0 * 50 ),
        Vector2( -61.5 * 50, -82 * 50 ), 
        Vector2(  61.5 * 50, -82 * 50 ),
        Vector2(  71.5 * 50,   0 * 50 )
    ]
    steer_normalize_epsilon = 0.005
    handbrake_cutoff        = 0.05
    slowdown_cutoff         = 0.25
    
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index
        self.waypoints = []
        
        
        # This should test the ability to make 180-degree turns
        # self.waypoints = [
        #    Vector2(61.5 * 50, 82 * 50),
        #    Vector2(-61.5 * 50, 82 * 50)
        # ]
        self.control_sequence = None
        
        # define some control sequences
        self.CTRLSEQ_HALF_FLIP = ControlSequence(30, self.CTRLSEQ_HALF_FLIP_f)


    def Dampen( self, steer, turn ):
        # Dampen the ringing.
        if ( abs(steer) > self.__class__.slowdown_cutoff ):
            return turn * 1.0
        else:
            return turn * ( abs(steer) / self.__class__.slowdown_cutoff )




    def NormalizeSteer( self, steer ):
        #May be using improper nomenclature
        if steer > self.__class__.steer_normalize_epsilon:
            return -1.0
        elif steer < self.__class__.steer_normalize_epsilon:
            return 1.0
        else:
            return 0.0




    def Require_Half_Flip( self, steer ):
        #self.control_sequence = self.CTRLSEQ_HALF_FLIP
        #result = self.control_sequence.get_output_vector()
        #print("first frame of half-flip: " + str(result))
        #return result
        return steer > pi / 2 and steer < 3 * pi / 2
            



    def Require_Handbrake( self, steer ):
        # determine conditions required for handbraking.
        if ( abs( steer ) > self.__class__.handbrake_cutoff ):
            return 1
        else:
            return 0





##    # define some control sequence functions
##    def CTRLSEQ_HALF_FLIP_f( self, frame_num ):
##        if (frame_num == 15):
##            return [
##                0.0,       # throttle
##                0.0,       # steer
##                0.0,       # pitch
##                0.0,       # yaw
##                0.0,       # roll
##                1,         # jump
##                0,         # boost
##                0          # handbrake
##                ]
##        else:
##            return  [
##                0.0,      # throttle
##                0.0,      # steer
##                0.0,       # pitch
##                0.0,       # yaw
##                0.0,       # roll
##                0,         # jump
##                0,         # boost
##                0          # handbrake
##                ]



    def GetCarData( self, game_tick_packet, destination ):
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector2( car.Location.X, car.Location.Y )
        car_direction = get_car_facing_vector(car)
        car_to_destination = destination - car_location
        return ( car, car_location, car_direction, car_to_destination )
        


    def GetCarDirection( self, game_tick_packet ):
        return get_car_facing_vector( game_tick_packet.gamecars[self.index] )


    def GetCarLocation( self, car ):
        car = game_tick_packet.gamecars[self.index]
        return Vector2( car.Location.X, car.Location.Y )


    def GetCarToDestination( self, location, destination ):
        return destination - location


        
    def path_to_position(self, game_tick_packet, destination):
        """
            Returns the controls to get to a particular spot.
            Returns None if already there.
        """
        car = game_tick_packet.gamecars[self.index]
        ##        car_location = Vector2( car.Location.X, car.Location.Y )
        ##        car_direction = get_car_facing_vector(car)
        ##        car_to_destination = destination - car_location
        
        steer_correction_radians = self.GetCarDirection( game_tick_packet ).correction_to( self.GetCarToDestination( game_tick_packet ) )

        
        # If we need to turn more than pi/2 radians but less than 3pi/2 radians, half flip first
        if self.RequireHalfFlip():
            print("Should half flip here!")
            self.control_sequence = self.CTRLSEQ_HALF_FLIP

        
        return [
            # Throttle:
            1.0,

            # Steer:
            self.Dampen( steer_correction_radians, self.NormalizeSteer( steer_correction_radians ) ),

            # Pitch:
            0.0,

            # Yaw:
            0.0,

            # Roll:
            0.0,

            # Jump:
            0,

            # Boost:
            1,

            # Handbrake
            self.RequireHandbrake( steer_corretion_radians )
        ]



        
    def get_output_vector(self, game_tick_packet):
    
        # handle control sequences
        """
        if ( self.control_sequence != None ):
            outvec = self.control_sequence.get_output_vector()
            if ( outvec == None ):
                self.control_sequence = None
            else:
                print( "Outputting from a control sequence: {}".format( outvec ) )
                return outvec
        """
    
        # Navigate to the next waypoint
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector2( car.Location.X, car.Location.Y )
        delta = car_location - self.waypoints[0]
            
        epsilon = 300
        distance = sqrt( delta.x ** 2 + delta.y ** 2 )
        if (distance < epsilon):
            self.waypoints = self.waypoints[1:] + [ self.waypoints[0] ]
            print( "Updating boost target to: {}".format( self.waypoints[0] ) )
            
        return self.path_to_position(game_tick_packet, self.waypoints[0])
    



def get_car_facing_vector(car):

    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
