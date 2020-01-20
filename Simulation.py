from math import pi, atan2

from rlutilities.mechanics import AerialTurn as RLU_AerialTurn
from rlutilities.mechanics import Aerial as RLU_Aerial
from rlutilities.mechanics import Jump as RLU_Jump
from rlutilities.mechanics import Dodge as RLU_Dodge
from rlutilities.simulation import Input
from rlutilities.simulation import Car as RLU_Car
from rlutilities.linear_algebra import axis_to_rotation, cross, dot, mat3, norm, vec3

from Conversions import vec3_to_Vec3, Vec3_to_vec3, rot_to_mat3
from Maneuvers import GroundTurn
from Miscellaneous import angle_to



class Simulation:

    def __init__( self,
                  time = None,
                  hitbox = None,
                  ball_contact = False,
                  car = None):

        self.time = time
        self.car = car
        self.hitbox = hitbox
        self.ball_contact = ball_contact


###########################################################################
#Simulation functions
###########################################################################

def dodge_simulation(end_condition = None,
                     car = None,
                     hitbox_class = None,
                     dodge = None,
                     ball = None,
                     game_info = None,
                     boost = True):

    '''
    Simulates an RLU dodge until the dodge ends, or one of pass_condition or fail_condtion are met.
    pass_condition means that the dodge does what we wanted.  Returns True and the RLU car state at the end
    fail_condition returns (False, None), meaning the dodge doesn't achieve the desired result.
    '''

    #Copy everything we need and set constants
    time = 0
    dt = 1/60
    car_copy = RLU_Car(car)
    dodge_copy = RLU_Dodge(car_copy)
    if dodge.target != None:
        dodge_copy.target = dodge.target        
    if dodge.direction != None:
        dodge_copy.direction = dodge.direction
    if dodge.preorientation != None:
        dodge_copy.preorientation = dodge.preorientation
    if dodge.duration != None:
        dodge_copy.duration = dodge.duration
    else:
        dodge_copy.duration = 0
    #Make sure there's time between the jump and the dodge so that we don't just keep holding jump   
    if dodge.delay != None:
        dodge_copy.delay = dodge.delay
    else:
        dodge_copy.delay = max(dodge_copy.duration + 2*dt, 0.05)

    #Adjust for non-octane hitboxes
    box = update_hitbox(car_copy, hitbox_class)

    #Loop until we hit end_condition or the dodge is over.
    while not end_condition(time, box, ball, game_info.team_sign):

        #Update simulations and adjust hitbox again
        time += dt
        dodge_copy.step(dt)
        controls = dodge_copy.controls
        if boost:
            controls.boost = 1
        car_copy.step(controls, dt)
        box = update_hitbox(car_copy, hitbox_class)

        if dodge_copy.finished:
            #If the dodge never triggers condition, give up and move on
            #TODO: give up sooner to save computation time
            return Simulation()

    return Simulation(ball_contact = True,
                      car = car_copy,
                      box = box,
                      time = time)

##############################################################

def stationary_ball_dodge_contact(game_info, contact_height):
    '''
    Returns dodge duration and delay so the car can reach contact_height
    '''

    ball = game_info.ball
    hitbox_class = game_info.me.hitbox_class
    car_copy = RLU_Car(game_info.utils_game.my_car)
    turn = RLU_AerialTurn(car_copy)
    turn.target = roll_away_from_target(ball.pos,
                                        pi/4,
                                        game_info)
    box = update_hitbox(car_copy, hitbox_class)
    time = 0
    dt = 1/60
    ball_contact = has_ball_contact(time, box, ball, game_info.team_sign)
    intended_contact_point = ball_contact[1]


    while intended_contact_point[2] < contact_height and not ball_contact[0]:
        time += dt
        turn.step(dt)
        controls = turn.controls
        if time <= 0.20:
            controls.jump = 1
        controls.boost = 1

        car_copy.step(controls, dt)
        box = update_hitbox(car_copy, hitbox_class)
        ball_contact = has_ball_contact(time, box, ball, game_info.team_sign)
        intended_contact_point = ball_contact[1]
        if time >= 1.45: #Max dodge time
            return None, None, Simulation()

    if not ball_contact[0]:
        return None, None, Simulation()
    if time < 0.2:
        duration = time
        delay = duration + 2*dt
    else:
        duration = 0.2
        delay = time

    delay -= 0.05 #How long before we hit the ball is acceptable to dodge

    return duration, delay, Simulation(ball_contact = True, car = car_copy, hitbox = box, time = time)


##############################################################
##############################################################

def moving_ball_dodge_contact(game_info):
    '''
    Returns dodge duration and delay so the car can reach contact_height
    '''

    ball = game_info.ball
    contact_height = ball.pos.z - 20
    hitbox_class = game_info.me.hitbox_class
    car_copy = RLU_Car(game_info.utils_game.my_car)
    turn = RLU_AerialTurn(car_copy)
    turn.target = roll_away_from_target(ball.pos,
                                        pi/4,
                                        game_info)
    box = update_hitbox(car_copy, hitbox_class)
    time = 0
    dt = 1/60
    ball_contact = has_ball_contact(time, box, ball, game_info.team_sign)
    closest_point = ball_contact[1]


    while closest_point[2] < contact_height and not ball_contact[0]:
        time += dt
        ball = game_info.ball_prediction.state_at_time(game_info.game_time + time)

        turn.step(dt)
        contact_height = ball.pos.z - 30
        controls = turn.controls
        if time <= 0.20:
            controls.jump = 1
        controls.boost = 1

        car_copy.step(controls, dt)
        box = update_hitbox(car_copy, hitbox_class)

        ball_contact = has_ball_contact(time, box, ball, game_info.team_sign)
        closest_point = ball_contact[1]
        if time >= 1.45: #Max dodge time
            return None, None, Simulation()

    if not ball_contact[0]:
        return None, None, Simulation()

    if time < 0.2:
        duration = time
        delay = duration + 2*dt
    else:
        duration = 0.2
        delay = time

    delay -= 0.05 #Window to dodge just before ball contact

    return duration, delay, Simulation(ball_contact = True, car = car_copy, hitbox = box, time = time)


##############################################################
##############################################################

def linear_time_to_reach(current_state,
                         location,
                         game_time):
    '''
    Returns how long it will take to drive to the given location.
    Currently supports only locations more or less directly in front, holding boost while we have it.
    '''

    distance = (location.to_2d() - current_state.pos.to_2d()).magnitude()

    sim_pos = 0
    sim_vel = current_state.vel.to_2d().magnitude()
    sim_time = game_time
    dt = 1/60 #Doesn't need to be the FPS, just a convenient value
    while sim_pos < distance:
        sim_pos += sim_vel*dt
        if current_state.boost > 33.3 * sim_time:
            accel = boost_acceleration(sim_vel)
        else:
            accel = throttle_acceleration(sim_vel)
        sim_vel += accel*dt
        sim_time += dt
    return sim_time


##############################################################
#Helper functions
##############################################################

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

    if speed < 2300:
        return 991.667 + throttle_acceleration(speed)
    else:
        return 0


def roll_away_from_target(target, theta, game_info):
    '''
    Returns an orientation mat3 for an air roll shot.  Turns directly away from the dodge direction (target) by angle theta
    Target can either be RLU vec3, or CowBot Vec3.
    '''

    starting_forward = game_info.utils_game.my_car.forward()
    starting_left = game_info.utils_game.my_car.left()
    starting_up = game_info.utils_game.my_car.up()
    starting_orientation = mat3(starting_forward[0], starting_left[0], starting_up[0],
                                starting_forward[1], starting_left[1], starting_up[1],
                                starting_forward[2], starting_left[2], starting_up[2])
    if type(target) == vec3:
        target = vec3_to_Vec3(target, game_info.team_sign)
    car_to_target = Vec3_to_vec3((target - game_info.me.pos).normalize(), game_info.team_sign)
    axis = theta * cross(car_to_target, starting_up)
    return dot(axis_to_rotation(axis), starting_orientation)




##############################################################
#Contact functions
##############################################################

def has_ball_contact(time, box, ball, team_sign):
    '''
    Returns whether or not box (RLU obb) intersects ball, and box's nearest point to the ball.
    '''

    contact_point = nearest_point(box, Vec3_to_vec3(ball.pos, team_sign))
    ball_contact = norm(contact_point - Vec3_to_vec3(ball.pos, team_sign)) < 92.75
    return ball_contact, contact_point


def nearest_point(box, point, local = False):
    '''
    Takes in an RLU oriented bounding box (obb) object and an RLU vec3.
    Returns an RLU vec3 for the closest point on box to point.
    local = True returns the vec3 in box's local coordinates
    '''
    
    point_local = dot(point - box.center, box.orientation)
    closest_point_local = vec3( min(max(point_local[0], -box.half_width[0]), box.half_width[0]),
                                    min(max(point_local[1], -box.half_width[1]), box.half_width[1]),
                                    min(max(point_local[2], -box.half_width[2]), box.half_width[2]) )

    if local:
        return closest_point_local
    return dot(box.orientation, closest_point_local) + box.center


def update_hitbox(car, hitbox_class):
    '''
    Calculates the hitbox of an RLU car object, and adjusts it for non-octane hitbox types
    Returns the correct RLU obb object for the car's hitbox
    '''

    #Update hitbox center
    box = car.hitbox()
    box.half_width = vec3(hitbox_class.half_widths[0],
                          hitbox_class.half_widths[1],
                          hitbox_class.half_widths[2])
    offset = vec3(hitbox_class.offset[0],
                  hitbox_class.offset[1],
                  hitbox_class.offset[2])
    box.center = dot(box.orientation, offset) + car.location
    return box



###########################################################################
#Face contact functions: front_face_contact, back, top, bottom.
###########################################################################


def front_face_contact(box, ball, team_sign):
    '''
    Checks if the nearest point is on the front face of the box.
    Should be used in conjunction with a ball_contact check
    '''

    contact_point_local = nearest_point(box, Vec3_to_vec3(ball.pos, team_sign), local = True)
    front_face_contact = (contact_point_local[0] > box.half_width[0] - 0.001)

    return front_face_contact

def back_face_contact(box, ball, team_sign):
    '''
    Checks if the nearest point is on the back face of the box.
    Should be used in conjunction with a ball_contact check
    '''

    contact_point_local = nearest_point(box, Vec3_to_vec3(ball.pos, team_sign), local = True)
    back_face_contact = (contact_point_local[0] < - box.half_width[0] + 0.001)

    return back_face_contact

def top_face_contact(box, ball, team_sign):
    '''
    Checks if the nearest point is on the top face of the box.
    Should be used in conjunction with a ball_contact check
    '''

    contact_point_local = nearest_point(box, Vec3_to_vec3(ball.pos, team_sign), local = True)
    top_face_contact = (contact_point_local[2] > box.half_width[2] - 0.001)

    return top_face_contact


def bottom_face_contact(box, ball, team_sign):
    '''
    Checks if the nearest point is on the bottom face of the box.
    Should be used in conjunction with a ball_contact check
    '''

    contact_point_local = nearest_point(box, Vec3_to_vec3(ball.pos, team_sign), local = True)
    bottom_face_contact = (contact_point_local[2] < - box.half_width[2] + 0.001)

    return bottom_face_contact


