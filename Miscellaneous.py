from math import pi
from math import log, cos, sin, asin

from rlutilities.linear_algebra import mat3, vec3
import rlbot.utils.game_state_util as framework

from CowBotVector import *

def one_frame_derivative(f, old_f, fps):
    return (f - old_f) / (1 / fps)


def cap_magnitude(x, magnitude):
    '''
    caps off a variable at a certain max magnitude.
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
        

#This is very broken, fix later.  For now I'm patching by just manually entering boost thresholds.
def find_final_vel(v_initial, boost_amount):
    '''
    This assumes going in a straight line and already moving in the forward direction.
    It returns the maximum speed we can reach by just holding boost, and using boost_amount
    '''

    v_max = 2275
    v_throttle = 1450
    boost_per_second = 33.3
    boost_accel = 1000

    if boost_amount < -(log(1-((v_throttle - v_initial)/(v_max)))):
        return v_max + ((v_initial - v_max)*exp(-(boost_amount / boost_per_second)))

    else:
        boost_remaining = boost_amount - log(1-((v_throttle - v_initial)/(v_max)))
        return min(v_max, v_throttle + boost_accel*(boost_remaining / boost_per_second))


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
    return abs(sin(angle1 - angle2)) < asin(epsilon)


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



def rot_to_mat3(rot):
    return mat3( rot.front.x, rot.left.x, rot.up.x,
                 rot.front.y, rot.left.y, rot.up.y,
                 rot.front.z, rot.left.z, rot.up.z )

def pyr_to_matrix(pyr):
    pitch = pyr[0]
    yaw = pyr[1]
    roll = pyr[2]

    front = Vec3(cos(yaw)*cos(pitch),
                 sin(yaw)*cos(pitch),
                 sin(pitch))
    left = Vec3(-cos(yaw)*sin(pitch)*sin(roll) - sin(yaw)*cos(roll),
                -sin(yaw)*sin(pitch)*sin(roll) + cos(yaw)*cos(roll),
                cos(pitch)*sin(roll))
    up = Vec3(-cos(yaw)*sin(pitch)*cos(roll) + sin(yaw)*sin(roll),
              -sin(yaw)*sin(pitch)*cos(roll) - cos(yaw)*sin(roll),
              cos(pitch)*cos(roll))
    
    return [front, left, up]


def Vec3_to_Vector3(vector):
    return framework.Vector3(x = vector.x, y = vector.y, z = vector.z)

def Vec3_to_vec3(vector):
    return vec3(vector.x, vector.y, vector.z)

def vec3_to_Vec3(vector):
    return Vec3(vector[0], vector[1], vector[2])
