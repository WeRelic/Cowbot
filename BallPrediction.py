from math import atan2, pi, tan

import rlutilities as utils
from rlutilities.mechanics import Aerial

from Conversions import vec3_to_Vec3, Vec3_to_vec3
from CowBotVector import Vec3

#############################################################################################
#
#############################################################################################

class PredictionPath:

    '''
    The ball prediction that CowBot's code will rely on.
    It is designed to be independent of the source of the prediction (for now, framework or RLU).
    All values going directly in or out should be in terms of CowBot types (e.g., Vec3), 
    and team-independent.
    '''

    def __init__(self,
                 ball_prediction = None,
                 utils_game = None,
                 condition = None,
                 source = None,
                 team = None):

        '''
        source is either "RLU" or "Framework" depending on where we pull our prediction from.
        '''

        team_sign = (team - (1/2)) * (-2)

        if source == "RLU":
            prediction = utils.simulation.Ball(utils_game.ball)

            #Assemble a list of the slices in our predicted path.
            self.slices = []
            #For the first slice, there is no previous slice.
            self.slices.append(RLUPredictionSlice(prediction, team_sign))
            i = 1
            while condition(self.slices):
                #For all other slices, we have a previous slice.
                prediction.step(1/60)
                self.slices.append(RLUPredictionSlice(prediction, team_sign))
                i +=1

        elif source == "Framework":

            self.slices = [ FrameworkPredictionSlice(frame, team_sign) for frame in ball_prediction.slices ]



    ######################
    #TODO: Check bouncing?
 

    def state_at_time(self, time):
        #Return the slice closest to the given time.
        for step in self.slices:
            #60 slices per second.  FPS check?
            if abs(step.time - time) <= 1/60:
                return step
        return None

    ######################

    def check_on_net(self):
        #Check if at some point the ball is between the posts and behind the goal line.
        for step in self.slices:
            if abs(step.x) < 800 and step.y > 5120 - 92.75:
                return "Attacking"
            elif abs(step.x) < 800 and step.y < -5120 - 92.75:
                return "Defending"
        return False



#############################################################################################
#
#############################################################################################

    
class RLUPredictionSlice:

    '''
    This class unpacks a frame of the RLU ball prediction and puts it in terms of CowBot variables.
    It also handles team checking so that we can always think of ourselves as on the blue team.
    '''


    
    def __init__(self,
                 current_slice,
                 team_sign):


        #Position, rotation, velocity, omega for the current slice
        self.x = current_slice.location[0] * team_sign
        self.y = current_slice.location[1] * team_sign
        self.z = current_slice.location[2]
        self.pos = Vec3(self.x, self.y, self.z)

        '''
        Irrelevant for a ball.  No idea if a puck will ever be supported.
        pitch = current_slice.pitch
        yaw = current_slice.yaw
        roll = current_slice.roll
        self.rot = Orientation(pyr = [ pitch, yaw, roll] )
        '''

        self.vx = current_slice.velocity[0] * team_sign
        self.vy = current_slice.velocity[1] * team_sign
        self.vz = current_slice.velocity[2]
        self.vel = Vec3(self.vx, self.vy, self.vz)

        self.omegax = current_slice.angular_velocity[0] * team_sign
        self.omegay = current_slice.angular_velocity[1] * team_sign
        self.omegaz = current_slice.angular_velocity[2]
        self.omega = Vec3(self.omegax, self.omegay, self.omegaz)

        self.time = current_slice.time


######################################################################################
#
######################################################################################

class FrameworkPredictionSlice:

    '''
    This class takes a slice of the framework ball prediction and puts it in terms of CowBot variables.
    It also handles team checking so that we can always think of ourselves as on the blue team.
    '''

    def __init__(self, current_slice,
                 team_sign):


        #Position, rotation, velocity, omega for the current slice
        self.x = current_slice.physics.location.x * team_sign
        self.y = current_slice.physics.location.y * team_sign
        self.z = current_slice.physics.location.z
        self.pos = Vec3(self.x, self.y, self.z)

        self.vx = current_slice.physics.velocity.x * team_sign
        self.vy = current_slice.physics.velocity.y * team_sign
        self.vz = current_slice.physics.velocity.z
        self.vel = Vec3(self.vx, self.vy, self.vz)

        self.omegax = current_slice.physics.angular_velocity.x * team_sign
        self.omegay = current_slice.physics.angular_velocity.y * team_sign
        self.omegaz = current_slice.physics.angular_velocity.z
        self.omega = Vec3(self.omegax, self.omegay, self.omegaz)

        self.time = current_slice.game_seconds




###############################################################################################
#Useful prediction functions - unrelated to the above classes.
###############################################################################################

def aerial_prediction(game_info, min_time, persistent):
    '''
    Checks where in the future an aerial will put us hitting the ball, and updates our persistent
    aerial object to have that time and place as the target data.
    '''

    prediction = game_info.ball_prediction

    for i in range(0, len(prediction.slices), 2):
        
        aerial = Aerial(game_info.utils_game.my_car)

        if prediction.slices[i].pos.z > 150:# and prediction.slices[i].time > min_time:
            aerial.target = Vec3_to_vec3(prediction.slices[i].pos, game_info.team_sign)
            aerial.arrival_time = prediction.slices[i].time
            simulation = aerial.simulate()
            if (vec3_to_Vec3(simulation.location, game_info.team_sign) - vec3_to_Vec3(aerial.target, game_info.team_sign)).magnitude() < 30:
                persistent.aerial.target_location = prediction.slices[i].pos
                persistent.aerial.target_time = prediction.slices[i].time
                break

    return persistent

############################################

def ground_prediction(game_info, persistent):
    '''
    Checks where in the future an aerial will put us hitting the ball, and updates our persistent
    aerial object to have that time and place as the target data.
    '''

    prediction = game_info.ball_prediction

    for i in range(0, len(prediction.slices), 2):
        
        if prediction.location.z < 150:
            persistent.hit_ball.action.target = prediction.location
            persistent.hit_ball.action.arrival_time = prediction.time
            if prediction.time - game_info.game_time > drive_time(game_info,
                                                                  prediction.location,
                                                                  game_info.me.boost):
                break

    return persistent

############################################

def get_ball_arrival(game_info,
                     condition):
    '''
    Returns the time and location at which the ball first satisfies condition.
    condition is a function that takes in a location and returns a Boolean.
    '''

    aerial = Aerial(game_info.utils_game.my_car)
    prediction = game_info.ball_prediction
    for i in range(0, len(prediction.slices), 2):

        if condition(prediction.slices[i].pos, prediction.slices[i].vel, game_info.team_sign):
            return prediction.slices[i].time, prediction.slices[i].pos

############################################

def choose_stationary_takeoff_time(game_info,
                                   target_loc,
                                   target_time):
    '''
    Decides when to take off for an aerial based on a given target time and place.
    Assumes we're sitting still to start with.
    '''

    aerial = Aerial(game_info.utils_game.my_car)

    aerial.target = Vec3_to_vec3(target_loc, game_info.team_sign)
    current_time = game_info.game_time
    test_interval = [current_time, target_time]
    while abs(test_interval[1] - test_interval[0]) > 1/30:
        test_time = (test_interval[0] + test_interval[1]) / 2
        aerial.arrival_time = test_time
        simulation = aerial.simulate()
        if vec3_to_Vec3(simulation.location - aerial.target, game_info.team_sign).magnitude() < 100:
            test_interval = [test_interval[0], test_time]
        else:
            test_interval = [test_time, test_interval[1]]
    return target_time - (test_interval[1] - current_time)


############################################

def is_ball_in_front_of_net(location):
    '''
    Returns whether or not the ball is in front of the net, disregarding y-coordinates.
    '''

    #Check if x is between +/- (goal width + ball radius)
    #and if z is below (goal height + ball radius- (fudge factor to avoid the crossbar))
    return (abs(location.x) < 893+92.75) and location.z < 642.775+92.75-20

############################################

def is_ball_in_scorable_box(loc,
                            vel,
                            theta_top = pi/6,
                            theta_side = pi/6,
                            max_distance = 1500):
    '''
    Returns whether location is in the angled box in front of net of the given dimensions
    '''

    goal_distance = loc.y + 5120
    if loc.x < 0:
        x_sign = -1
    else:
        x_sign = 1

    near_post_vector = Vec3(x_sign*920, -5120, 0) - Vec3(loc.x, loc.y, 0)
    far_post_vector = Vec3(-x_sign*920, -5120, 0) - Vec3(loc.x, loc.y, 0)

    angle_to_near_post = atan2(near_post_vector.y, near_post_vector.x)
    angle_to_far_post = atan2(far_post_vector.y, far_post_vector.x)
    ball_towards_net = (x_sign*angle_to_far_post < x_sign*atan2(vel.y, vel.x) < x_sign*angle_to_near_post)

    if loc.y > -5120 + max_distance:
        #If the ball is far away from the net, it's not scorable
        return False
    elif abs(loc.x) > 893 + goal_distance*tan(theta_side):
        #If the ball is far to the side, the angle is too tight to score
        return False
    elif loc.z > 642.775 + goal_distance*tan(theta_top):
        #If the ball is too high, the angle is too tight to score
        return False
    elif not ball_towards_net and loc.z < 150:
        return False
    else:
        return True


#TODO: Add time estimates for getting to the ball, and predicting when it'll roll into the center of the field.  This will let us take shots more reliably, since we'll be getting there _before_ it rolls out of reach.

