import math

URotationToRadians = math.pi / float(32768)

# A control sequence allows a subroutine to take over planning for the agent
# for a number of frames. This is useful for things like half-flipping, etc.
class ControlSequence:
    def __init__(self, num_frames, f):
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
    def __init__(self, name, team, index):
        self.name = name
        self.team = team  # 0 towards positive goal, 1 towards negative goal.
        self.index = index
        
        # This is the boosts in order
        self.waypoints = [Vector2(61.5 * 50, 82 * 50), Vector2(-61.5 * 50, 82 * 50), Vector2(-71.5 * 50,0 * 50), Vector2(-61.5 * 50, -82 * 50), Vector2(61.5 * 50,-82 * 50), Vector2(71.5 * 50,0 * 50)]
        # This should test the ability to make 180-degree turns
        #self.waypoints = [Vector2(61.5 * 50, 82 * 50), Vector2(-61.5 * 50, 82 * 50)]
        self.control_sequence = None
        
        # define some control sequences
        self.CTRLSEQ_HALF_FLIP = ControlSequence(30, self.CTRLSEQ_HALF_FLIP_f)
        
    # define some control sequence functions
    def CTRLSEQ_HALF_FLIP_f(self, frame_num):
        if (frame_num == 15):
            return [
                0.0,      # throttle
                0.0,      # steer
                0.0,       # pitch
                0.0,       # yaw
                0.0,       # roll
                1,         # jump
                0,         # boost
                0          # handbrake
                ]
        else:
            return  [
                0.0,      # throttle
                0.0,      # steer
                0.0,       # pitch
                0.0,       # yaw
                0.0,       # roll
                0,         # jump
                0,         # boost
                0          # handbrake
                ]
        
    # Returns the controls to get to a particular spot. Returns None if already there.
    def path_to_position(self, game_tick_packet, destination):
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector2(car.Location.X, car.Location.Y)
        car_direction = get_car_facing_vector(car)
        car_to_destination = destination - car_location
        
        steer_correction_radians = car_direction.correction_to(car_to_destination)
        
        # If we need to turn more than pi/2 radians but less than 3pi/2 radians, half flip first
        if (steer_correction_radians > math.pi/2 and 
            steer_correction_radians < 3 * math.pi/2):
            #self.control_sequence = self.CTRLSEQ_HALF_FLIP
            print("Should half flip here!")
            #result = self.control_sequence.get_output_vector()
            #print("first frame of half-flip: " + str(result))
            #return result
        
        epsilon = 0.005
        if steer_correction_radians > epsilon:
            turn_direction = -1.0
        elif steer_correction_radians < epsilon:
            turn_direction = 1.0
        else:
            turn_direction = 0.0
        
        # Dampen the ringing.
        slowdown_cutoff = 0.25
        if (abs(steer_correction_radians) > slowdown_cutoff):
            turn = turn_direction * 1.0
        else:
            turn = turn_direction * (abs(steer_correction_radians)/slowdown_cutoff)
            
        # To speed up turns, we can engage the handbrake
        handbrake_cutoff = 0.5
        if (abs(steer_correction_radians) > handbrake_cutoff):
            handbrake = 1
        else:
            handbrake = 0
        
        return [
            1.0,       # throttle
            turn,      #steer
            0.0,       # pitch
            0.0,       # yaw
            0.0,       # roll
            0,         # jump
            1,         # boost
            handbrake  # handbrake
        ]
        
    def get_output_vector(self, game_tick_packet):
    
        # handle control sequences
        """
        if (self.control_sequence != None):
            outvec = self.control_sequence.get_output_vector()
            if (outvec == None):
                self.control_sequence = None
            else:
                print("Outputting from a control sequence: " + str(outvec))
                return outvec
        """
    
        # Navigate to the next waypoint
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector2(car.Location.X, car.Location.Y)
        delta = car_location - self.waypoints[0]
            
        epsilon = 300
        distance = math.sqrt(delta.x ** 2 + delta.y ** 2)
        if (distance < epsilon):
            self.waypoints = self.waypoints[1:] + [self.waypoints[0]]
            print("Updating boost target to: " + str(self.waypoints[0]))
            
        return self.path_to_position(game_tick_packet, self.waypoints[0])
    

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
        # The in-game axes are left handed, so use -x
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


def get_car_facing_vector(car):

    pitch = float(car.Rotation.Pitch)
    yaw = float(car.Rotation.Yaw)

    facing_x = math.cos(pitch * URotationToRadians) * math.cos(yaw * URotationToRadians)
    facing_y = math.cos(pitch * URotationToRadians) * math.sin(yaw * URotationToRadians)

    return Vector2(facing_x, facing_y)
