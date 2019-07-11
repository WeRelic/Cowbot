from math import atan2, pi, tan

import rlutilities as utils
from rlutilities.mechanics import Aerial

from Conversions import vec3_to_Vec3, Vec3_to_vec3
from CowBotVector import Vec3


class BallPredictionSlice:

    def __init__(self, current_slice, prev_slice):


        #Position, rotation, velocity, omega for the current slice
        self.x = current_slice.location[0]
        self.y = current_slice.location[1]
        self.z = current_slice.location[2]
        self.pos = Vec3(self.x, self.y, self.z)

        '''
        Irrelevant for a ball.  No idea if a puck will ever be supported.
        pitch = current_slice.pitch
        yaw = current_slice.yaw
        roll = current_slice.roll
        self.rot = Orientation(pyr = [ pitch, yaw, roll] )
        '''

        self.vx = current_slice.velocity[0]
        self.vy = current_slice.velocity[1]
        self.vz = current_slice.velocity[2]
        self.vel = Vec3(self.vx, self.vy, self.vz)

        self.omegax = current_slice.angular_velocity[0]
        self.omegay = current_slice.angular_velocity[1]
        self.omegaz = current_slice.angular_velocity[2]
        self.omega = Vec3(self.omegax, self.omegay, self.omegaz)

        self.time = current_slice.time

        ########################################################

        if prev_slice != None:

            #Position, rotation, velocity, omega for the previous slice,
            #assuming we have a previous slice
            self.old_x = prev_slice.pos.x
            self.old_y = prev_slice.pos.y
            self.old_z = prev_slice.pos.z
            self.old_pos = Vec3(self.x, self.y, self.z)

            '''
            Irrelevant for a ball.  No idea if a puck will ever be supported.
            old_pitch = prev_slice.rotation.pitch
            old_yaw = prev_slice.rotation.yaw
            old_roll = prev_slice.rotation.roll
            self.old_rot = Orientation(pyr = [ old_pitch, old_yaw, old_roll] )
            '''

            self.old_vx = prev_slice.vel.x
            self.old_vy = prev_slice.vel.y
            self.old_vz = prev_slice.vel.z
            self.old_vel = Vec3(self.vx, self.vy, self.vz)

            self.old_omegax = prev_slice.omega.x
            self.old_omegay = prev_slice.omega.y
            self.old_omegaz = prev_slice.omega.z
            self.old_omega = Vec3(self.old_omegax, self.old_omegay, self.old_omegaz)

            self.old_time = prev_slice.time

        ########################################################


    def check_rolling(self):
        #Add in a check if contact surface speed is zero.  This needs RLU to find the contact point.
        return False


    def check_bounce(self):

        #Three states: Rolling, Bouncing, Neither.  If we're rolling, we're not bouncing.
        if self.check_rolling():
            return False
        else:
            #Check if acceleration is close to that of just gravity.
            #If it is, then we're at a bounce.
            epsilon = 25
            gravity_accel = -650
            ball_accel = self.vel - self.prev_vel
            if abs(gravity_accel - ball_acel) / (self.current_time - self.old_time) > epsilon:
                return True
            else:
                return False



#############################################################################################

#############################################################################################



class PredictionPath:

    def __init__(self, utils_game, condition):
        prediction = utils.simulation.Ball(utils_game.ball)

        #Assemble a list of the slices in our predicted path.
        self.slices = []
        #For the first slice, there is no previous slice.
        self.slices.append(BallPredictionSlice(prediction, None))
        i = 1
        while condition(self.slices):
            #For all other slices, we have a previous slice.
            prediction.step(1/60)
            self.slices.append(BallPredictionSlice(prediction, self.slices[i - 1]))
            i +=1 


    ######################

    def state_at_time(self, time):
        #Return the slice closest to the given time.
        for step in self.slices:
            #60 slices per second.  FPS check?
            if abs(step.time - time) <= 1/60:
                return step
        #If time is too far in the future, it won't be in the prediction
        #print("Time called is beyond prediction time")
        return None

    ######################

    def check_on_net(self):
        #Check if at some point the ball is between the posts and behind the goal line.
        for step in self.slices.keys():
            if abs(step.x) < 800 and step.y > 5120 -92.75:
                return "Orange"
            elif abs(step.x) < 800 and step.y < -5120 -92.75:
                return "Blue"
        return False

    ######################

    def check_corner(self):
        #Eventually this will tell me if the ball is going into a corner (and staying there?),
        #and if so, which one
        return False

    ######################

    def bounces(self):
        #Returns a list of slices in which the ball bounces
        bounces = []
        for step in self.slices:
            if step.check_bouncing():
                bounces.append(step)
        return bounces






###############################################################################################
#Useful prediction functions
###############################################################################################



def aerial_prediction(game_info, min_time, persistent):
    '''
    Checks where in the future an aerial will put us hitting the ball, and updates our persistent
    aerial object to have that time and place as the target data.
    '''
    prediction = utils.simulation.Ball(game_info.utils_game.ball)
    

    for i in range(100):

        aerial = Aerial(game_info.utils_game.my_car)

        prediction.step(1/60)
        prediction.step(1/60)

        if prediction.location[2] > 150:# and prediction.time > min_time:
            aerial.target = prediction.location
            aerial.arrival_time = prediction.time
            simulation = aerial.simulate()
            if (vec3_to_Vec3(simulation.location, game_info.team_sign) - vec3_to_Vec3(aerial.target, game_info.team_sign)).magnitude() < 30:
                persistent.aerial.target_location = prediction.location
                persistent.aerial.target_time = prediction.time
                break

    return persistent

############################################

def ground_prediction(game_info, persistent):
    '''
    Checks where in the future an aerial will put us hitting the ball, and updates our persistent
    aerial object to have that time and place as the target data.
    '''
    prediction = utils.simulation.Ball(game_info.utils_game.ball)

    for i in range(100):
        
        prediction.step(1/60)

        if prediction.location[2] > 150:
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
    prediction = utils.simulation.Ball(game_info.utils_game.ball)
    
    for i in range(200):

        prediction.step(1/60)
        prediction.step(1/60)

        if condition(vec3_to_Vec3(prediction.location, game_info.team_sign), vec3_to_Vec3(prediction.velocity, game_info.team_sign)):
            return prediction.time, vec3_to_Vec3(prediction.location, game_info.team_sign)

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

############################################


def check_on_goal(pred, time):
    '''
    Returns if the ball will be in the net within time (just looks at y-coordinates)
    '''
    on_net = False
    i = 0
    while pred.slices[i].time < time:
        if pred.slices[i].pos.y < -(5120+92.75):
            on_net = True
            break

        i +=1
    return on_net



#TODO: Add time estimates for getting to the ball, and predicting when it'll roll into the center of the field.  This will let us take shots more reliably, since we'll be getting there _before_ it rolls out of reach.

