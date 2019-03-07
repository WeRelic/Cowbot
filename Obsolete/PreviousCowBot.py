import math, random

URotationToRadians = math.pi / float(32768)
            
class Waypoint:

    def __init__(self, x, y, z, ref_frame="pitch"):
        self.destination = Vector3(x, y, z)
        self.ref_frame = ref_frame
        
    def get_destination(self, game_tick_packet):
        """
        Returns a Vec3 relative to a reference frame.
        """
        if (self.ref_frame == "pitch"):
            return self.destination
        elif (self.ref_frame == "ball"):
            ball = game_tick_packet.gameball
            ball_pos = Vector3(ball.Location.X, ball.Location.Y, ball.Location.Z)
            return ball_pos + self.destination
        else:
            return self.destination # default case

class Agent:
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index
        self.framecnt = 0
        
        self.waypoints = [Waypoint(0,0,0,"ball")]
        self.control_sequences = [self.ctrlseq_wildly_throw_self]
    
    #####################################################
    #  Control sequences return None to release control #
    #####################################################
    '''
    Return in format 
    [
            float in [-1,1],       # throttle
            float in [-1,1],       # steer
            float in [-1,1],       # pitch
            float in [-1,1],       # yaw
            float in [-1,1],       # roll
            Boolean in {0,1},      # jump
            Boolean in {0,1},      # boost
            Boolean in {0,1}       # drift
        ]
    '''        
        
    def get_output_vector(self, game_tick_packet):
    
        # Don't try to start anything until you have control
        if (not game_tick_packet.gameInfo.bRoundActive):
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0]
    
        # handle control sequences
        if (len(self.control_sequences) > 0):
            outvec = self.control_sequences[0](self, self.framecnt)
            # If the return value is None, then the control sequence is releasing control
            if (outvec == None):
                self.control_sequences = self.control_sequences[1:] # DEBUG: do the first one over and over again.
                self.framecnt = 0
                return(self.get_output_vector(game_tick_packet))
            else:
                self.framecnt += 1
                return outvec
                
    
        # If we don't have a control sequence, navigate to the next waypoint
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector3(car.Location.X, car.Location.Y, car.Location.Z)
        delta = car_location - self.waypoints[0].get_destination(game_tick_packet)
            
        epsilon = 300
        distance = math.sqrt(delta.x ** 2 + delta.y ** 2)
        if (distance < epsilon):
            self.waypoints = self.waypoints[1:] + [self.waypoints[0]]
            #print("Updating boost target to: " + str(self.waypoints[0]))
            
        return self.path_to_position(game_tick_packet, self.waypoints[0].get_destination(game_tick_packet))

    
class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2( self.x + val.x, self.y + val.y)

    def __sub__(self,val):
        return Vector2( self.x - val.x, self.y - val.y)
        
    def __str__(self):
        return '{' + str(self.x) + ', ' + str(self.y) + '}'

    def correction_to(self, ideal):
        # Angle starts at the y-axis, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction
        
class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __add__(self, val):
        return Vector3(self.x + val.x, self.y + val.y, self.z + val.z)
    
    def __sub__(self, val):
        return Vector3(self.x - val.x, self.y - val.y, self.z - val.z)
        
    def __str__(self):
        return '{' + ', '.join([self.x, self.y, self.z]) + '}'
        
    # TODO: 3D rotations
    def correction_to(self, ideal):

        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction

#TODO: Check these.  Work in Roll to get full car orientation.
def get_car_facing_vector(car):

    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)
    facing_z = math.sin(0.5 * pitch * URotationToRadians)

    return Vector3(facing_x, facing_y, facing_z)
