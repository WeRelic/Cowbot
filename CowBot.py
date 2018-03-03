import math

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
        self.control_sequences = [self.ctrlseq_front_flip]
    
    #  Control sequences return None to release control
    def ctrlseq_front_flip(self, game_tick_packet, framecnt):
        if (framecnt > 0 and framecnt < 10):
            return [0.0, 0.0, 0.0, 0.0, 0.0, 1, 0, 0]
        elif (framecnt < 20):
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0]
        else:
            return None
            
    # Returns the controls to get to a particular spot.
    def path_to_position(self, game_tick_packet, destination):
        car = game_tick_packet.gamecars[self.index]
        car_location = Vector3(car.Location.X, car.Location.Y, car.Location.Z)
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
        
        # Convert steering correction to a turning direction
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
            turn,      # steer
            0.0,       # pitch
            0.0,       # yaw
            0.0,       # roll
            0,         # jump
            1,         # boost
            handbrake  # handbrake
        ]
        
        
    def get_output_vector(self, game_tick_packet):
    
        # handle control sequences
        if (len(self.control_sequences) > 0):
            outvec = self.control_sequences[0](self, self.framecnt)
            # If the return value is None, then the control sequence is releasing control
            if (outvec == None):
                #self.control_sequences = self.control_sequences[1:] # DEBUG: do the first one over and over again.
                self.framecnt = 0
                return(self.get_output_vector(game_tick_packet))
            else:
                self.framecnt += 1
                print("Outputting from a control sequence: " + str(outvec))
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
        
    # TODO: this is slightly more interesting in 3D, so keeping the 2D version for now
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