from functools import partial
from math import pi, log, cos, sin, asin, atan2


#from rlutilities.linear_algebra import mat3, vec3
import rlbot.utils.game_state_util as framework

from CowBotVector import Vec3


def cap_magnitude(x, magnitude = 1):
    '''
    Caps off a variable at a certain max magnitude.
    Will be mostly used with magnitude = 1.
    '''
    if x > magnitude:
        return magnitude
    elif x < - magnitude:
        return - magnitude
    return x


def rotate_to_range(theta, interval):
    '''
    If theta isn't in range, then add or subtract the interval length as appropriate to
    ensure that it is
    '''

    while theta < interval[0]:
        theta += (interval[1] - interval[0])
    while theta > interval[1]:
        theta -= (interval[1] - interval[0])
    return theta
        
'''
#TODO: This is very broken, fix later.  For now I'm patching by just manually entering boost thresholds.
def find_final_vel(v_initial, boost_amount):

    This assumes going in a straight line and already moving in the forward direction.
    It returns the maximum speed we can reach by just holding boost, and using boost_amount


    v_max = 2275
    v_throttle = 1450
    boost_per_second = 33.3
    boost_accel = 1000

    if boost_amount < -(log(1-((v_throttle - v_initial)/(v_max)))):
        return v_max + ((v_initial - v_max)*exp(-(boost_amount / boost_per_second)))

    else:
        boost_remaining = boost_amount - log(1-((v_throttle - v_initial)/(v_max)))
        return min(v_max, v_throttle + boost_accel*(boost_remaining / boost_per_second))
'''

def find_closest_big_boost(game_info):
    min_boost_dist = 20000
    for boost in game_info.big_boosts:
        if (game_info.me.pos - boost.pos).magnitude() < min_boost_dist:
            if boost.is_active:
                min_boost_dist = (game_info.me.pos - boost.pos).magnitude()
                closest_boost = boost



def car_coordinates_2d(current_state, direction):
    '''
    Takes a Vec3 for a direction on the field and returns the same direction relative to the car
    '''

    x = direction.x * cos(-current_state.rot.yaw) - direction.y * sin(-current_state.rot.yaw)
    y = direction.x * sin(-current_state.rot.yaw) + direction.y * cos(-current_state.rot.yaw)
        
    return Vec3(x,y,0)


def angles_are_close(angle1, angle2, epsilon):
    '''
    Checks if two angles are close, without worrying about branches.
    '''
    return abs(angle_difference(angle1, angle2)) < epsilon



def angle_difference(angle1, angle2):
    '''
    Returns the smaller angle between two given angles, taking into account branches
    '''
    return rotate_to_range(angle1 - angle2, [-pi,pi])



def left_or_right(current_state, target_pos):
    '''
    Takes the current car state and where we want to go and says if that target is to the
    left (-1) or to the right (1).
    Only for angles < 2*pi/3
    '''

    target_angle = atan2((current_state.pos - target_pos).y, (current_state.pos - target_pos).x)
    if sin(target_angle) > 0:
        return 1
    else:
        return -1


def is_in_map(location):
    '''
    Checks if a Vec3 is in the map or not
    '''

    if abs(location.x) > 4096:
        return False
    if abs(location.y) > 5120:
        return False
    if location.z > 2044:
        return False
    if location.z < 0:
        return False
    return True


def angle_to(target, start, initial_angle):
    '''
    Take a location, and a location/yaw pair and returns the angle of turn needed.
    '''

    
    angle_to_target = atan2(target.y - start.y , target.x - start.x)
    return rotate_to_range(angle_to_target - initial_angle, [-pi,pi])



def min_radius(speed):
    '''
    Returns the maximum achievable curvature of a turn at a given velocity.
    This comes from Chip's notes. Powerslide is not considered.
    '''

    if speed <= 500:
        max_curvature = 0.0069 + ( speed * (1/500) * (0.00398 - 0.0069) )

    elif speed <= 1000:
        max_curvature = 0.00398 + ( (speed-500) * (1/500) * (0.00235 - 0.00398) )

    elif speed <= 1500:
        max_curvature = 0.00235 + ( (speed-1000) * (1/500) * (0.001375 - 0.00235) )

    elif speed <= 1750:
        max_curvature = 0.001375 + ( (speed-1500) * (1/250) * (0.0011 - 0.001375) )

    elif speed <= 2300:
        max_curvature = 0.0011 + ( (speed-1750) * (1/550) * (0.00088 - 0.0011) )


    return 1/max_curvature




def max_speed(radius):
    '''
    Returns the maximum achievable speed of a turn of a given radius.
    This comes from Chip's notes. Powerslide is not considered.
    '''

    curvature = 1/radius

    if curvature >= 0.00088:
        max_curvature = 2300 - ( (curvature-0.00088) * (1/550) * (0.00088 - 0.0011) )

    elif curvature >= 0.0011:
        max_curvature = 1750 - ( (curvature-0.0011) * (1/250) * (0.0011 - 0.001375) )

    elif curvature >= 0.001375:
        max_curvature = 1500 - ( (curvature-0.001375) * (1/500) * (0.001375 - 0.00235) )

    elif curvature >= 0.00235:
        max_curvature = 1000 - ( (curvature-0.00235) * (1/500) * (0.00235 - 0.00398) )

    elif curvature >= 0.00088:
        max_curvature = 500 - ( (curvature-0.00398) * (1/500) * (0.000398 - 0.0069) )


    return 1/max_curvature



def throttle_acceleration(speed, throttle = 1.0):
    '''
    Returns the acceleration from a given throttle in [0,1]
    Assume we are driving parallel to "forward", positive is forward, negative is backward
    '''

    if speed < 0:
        return 3500
    elif speed < 1400:
        return 1600 - (speed*( (1600-160)/1400 ))
    elif speed < 1410:
        return 160 - ( speed*(160/10) )
    else:
        return 0

def boost_acceleration(speed):
    '''
    Returns the acceleration from a given throttle in [0,1]
    Assume we are driving straight in the direction of the throttle.
    '''

    if speed < 2310:
        return 991.667 + throttle_acceleration(speed)
    else:
        return 0



def linear_time_to_reach(game_info,
               location):
    '''
    Returns how long it will take to drive to the given location.
    Currently supports only locations more or less directly in front, holding boost while we have it.
    '''

    distance = (location.to_2d() - game_info.me.pos.to_2d()).magnitude()

    sim_pos = 0
    sim_vel = game_info.me.vel.magnitude()
    sim_time = game_info.game_time
    dt = 1/120 #Doesn't need to be the FPS, just a convenient value
    while sim_pos < distance:
        sim_pos += sim_vel*dt
        if game_info.me.boost > 33.3 * sim_time:
            accel = boost_acceleration(sim_vel)
        else:
            accel = throttle_acceleration(sim_vel)
        sim_vel += accel*dt
        sim_time += dt
    return sim_time



###########################

def check_in_net(pos):
    '''
    Checks if a car position counts as "in net" when looking for teammates.
    '''
    if abs(pos.x) > 880:
        return False
    if pos.y > -5120+150:
        return False
    if pos.z > 650:
        return False
    return True

###########################


def check_far_post(pos, ball_x_sign):
    '''
    Checks if a car position counts as "far post" when looking for teammates.
    x_sign marks which side of the field the ball is on, so that we know what the far post is
    '''
    if (pos - Vec3(-ball_x_sign*1150)).magnitude() < 500:
        return True
    return False

###########################


#Functions to return a condition for ball prediction
def condition(pred = None, max_time = None):
    if pred[-1].time - pred[0].time < max_time:
        return True
    else:
        return False



def predict_for_time(time):
    return partial(condition, max_time = time)

