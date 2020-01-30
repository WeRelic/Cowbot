from math import atan2, pi, tan

import rlutilities as utils
from rlutilities.mechanics import Aerial, FollowPath

from Conversions import vec3_to_Vec3, Vec3_to_vec3
from CowBotVector import Vec3
from Miscellaneous import min_radius
from Pathing.ArcLineArc import ArcLineArc
from Pathing.PathPlanning import shortest_arclinearc
from Simulation import linear_time_to_reach


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
        self.ball_radius = 92.75

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
    #TODO: Check rolling

    def state_at_time(self, time):
        #Return the slice closest to the given time.
        for step in self.slices:
            #60 slices per second.
            if abs(step.time - time) <= 1/35:
                return step
        return None

    ######################

    def check_on_net(self):
        #Check if at some point the ball is between the posts and behind the goal line.
        for step in self.slices:
            if abs(step.x) < 800 and step.y > 5120 + self.ball_radius:
                return 1, step.time
            elif abs(step.x) < 800 and step.y < -5120 - self.ball_radius:
                return -1, step.time
        return False, None

    ######################

    def check_bounces(self):
        '''
        Return the times when the ball is bouncing
        TODO: General bounce, not just on flat ground
        '''

        bounces = []

        for i in range(1, len(self.slices)):
            if abs(self.slices[i].vel.z - self.slices[i-1].vel.z) > 50:
                bounces.append(self.slices[i])
        return bounces


     ######################

    def check_rolling(self):
        #TODO: Make this work in more general circumstances
        rolling = []
        for i in range(1, len(self.slices)):
            if abs(self.slices[i].omega.magnitude() * self.ball_radius - self.slices[i].vel.magnitude()) < 10:
                rolling.append(self.slices[i])
        return rolling

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

def rendezvous_prediction(game_info, min_time, persistent):
    '''
    Updates the place and time we will be contacting the ball
    '''

    prediction = game_info.ball_prediction

    for i in range(0, len(prediction.slices), 2):
        
        aerial = Aerial(game_info.utils_game.my_car)
        
        #if prediction.slices[i].pos.z > 150:# and prediction.slices[i].time > min_time:
        aerial.target = Vec3_to_vec3(prediction.slices[i].pos, game_info.team_sign)
        aerial.arrival_time = prediction.slices[i].time
        simulation = aerial.simulate()
        if (vec3_to_Vec3(simulation.location, game_info.team_sign) - vec3_to_Vec3(aerial.target, game_info.team_sign)).magnitude() < 30:
            persistent.aerial.target_location = prediction.slices[i].pos
            persistent.aerial.target_time = prediction.slices[i].time
            break

        #else:
        ''' This currently isn't defined, so we're going to skip it for now.
        if prediction.time - game_info.game_time > drive_time(game_info,
        prediction.location,
        game_info.me.boost):
        persistent.hit_ball.action.target = prediction.location
        persistent.hit_ball.action.arrival_time = prediction.time
        break
        '''

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

    ball_radius = 92.75
    #Check if x is between +/- (goal width + ball radius)
    #and if z is below (goal height + ball radius- (fudge factor to avoid the crossbar))
    return (abs(location.x) < 893+ball_radius) and location.z < 642.775+ball_radius-20


############################################

def when_is_ball_shootable(current_state = None,
                           prediction = None,
                           condition = None):

    '''
    Checks if we will be able to shoot the ball in the near future, and returns the prediction slice
    of the rendezvous.
    condition should take in current_state and a ball_slice and return a Boolean for 
    whether we can reach the ball to take a shot
    '''

    #TODO: Binary search
    for ball_slice in prediction.slices:
        if condition(current_state = current_state, ball_slice = ball_slice):
            return True, ball_slice
    return False, None


############################################

def is_ball_shootable(current_state = None,
                      ball_slice = None):

    '''
    Checks if a ball prediction slice is shootable on net given our car's current state.
    This will need to be improved over time.  I'm starting with a very coarse approximation.
    '''

    relative_ball_position = (ball_slice.pos - current_state.pos)
    return is_ball_in_front_of_net(ball_slice.pos) and relative_ball_position.y > 100


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


def prediction_binary_search(game_info = None, is_too_early = None):

    '''
    Returns the first ball prediction slice that is not "too early", judged by is_too_early
    is_too_early takes in a CarState and a ball prediction slice
    '''

    if len(game_info.ball_prediction.check_bounces()) == 0:
        prediction = game_info.ball_prediction.slices
    else:
        prediction = game_info.ball_prediction.check_bounces()
    low = 0
    high = len(prediction) - 1
    check = None, None, None

    while low < high:
        mid = (low + high) // 2
        new_check = is_too_early(game_info = game_info,
                                 index = game_info.my_index,
                                 target_time = prediction[mid].time,
                                 target_pos = prediction[mid].pos)
        if new_check[0]:
            low = mid + 1
        else:
            check = new_check
            high = mid
    return prediction[low], check[1], check[2]



############################################


def ball_contact_binary_search(game_info = None,
                               end_tangent = None):

    '''
    Finds a point we can path to, such that we can hand off to the ball contact code 
    in time for that to run properly
    '''

    end_tangent = end_tangent.normalize()
    bounce_list = game_info.ball_prediction.check_bounces()
    rolling_list = game_info.ball_prediction.check_rolling()
    if len(bounce_list) == 0:
        prediction = game_info.ball_prediction.slices
    else:
        prediction = bounce_list
        prediction.extend(rolling_list)
    low = 0
    high = len(prediction) - 1
    check = None, None, None

    while low < high:
        mid = (low + high) // 2
        #TODO: Take car velocity into account
        #prediction is only bounces if ball is bouncing
        #target_time, target_pos = find_handoff_point(game_info.ball_prediction, prediction, mid, end_tangent)

        new_check = shortest_arclinearc(game_info = game_info,
                                        target_time = prediction[mid].time, #target_time,
                                        target_pos = prediction[mid].pos, #target_pos,
                                        end_tangent = end_tangent)
        if new_check[0]:
            low = mid + 1
        else:
            check = new_check
            high = mid
    return prediction[low], check[1], check[2]


###########################################################################################
###########################################################################################


def linear_is_too_early(game_info, index, prediction_slice):
    '''
    Leaving index as an option so that we can check opponents and teammates too
    '''
    drive_time = linear_time_to_reach(game_info.me,
                                      game_info.ball.pos,
                                      game_info.game_time)
    return drive_time > prediction_slice.time

###############################################

def find_next_bounce(prediction, time):
    '''
    Returns the first bounce in the ball prediction after the current time
    '''

    bounces = prediction.check_bounces()
    for i in range(len(bounces)):
        if bounces[i].time > time:
            return bounces[i]

###############################################

def ball_changed_course(game_info = None,
                        plan = None,
                        persistent = None):
    '''
    Returns True if the ball is no longer going to be within reach of our current path
    by time we get there.
    '''

    expected_target = persistent.path_follower.end
    expected_target_time = persistent.path_follower.action.arrival_time

    #Where is the ball actually going to be when we're expecting to hit it?
    #One of these could be None in some situations?

    if game_info.game_time > expected_target_time:
        return True
    actual_target = game_info.ball_prediction.state_at_time(expected_target_time)

    print("actual: ", actual_target)
    print("Expected: ", expected_target)

    return (expected_target - actual_target).magnitude() > 50


###############################################


def find_handoff_point(ball_prediction, candidates, index, direction):
    '''
    ball_prediction will be the entire prediction for the ball's path
    candidates will be the points we're considering hitting (e.g., bounces)
    '''

    position = candidates[index].pos
    time = candidates[index].time - 0.2

    ball_slice = ball_prediction.state_at_time(time+0.1)
    if ball_slice != None:
        takeoff_distance = ball_slice.pos.z / (tan(pi/4))
        position = ball_slice.pos - direction.scalar_multiply(takeoff_distance)

    return time, position





