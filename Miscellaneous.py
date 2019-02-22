from math import pi
from math import log

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
    If theta isn't in range, then add or subtract 2*pi as appropriate to
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
