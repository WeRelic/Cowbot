from math import atan2

from BallPrediction import get_ball_arrival, when_is_ball_shootable, is_ball_in_scorable_box, is_ball_shootable
from Miscellaneous import is_drivable_point

from CowBotVector import Vec3

def ball(plan, game_info, persistent):
    '''
    Decides when to break from "Ball" state.
    '''

    current_state = game_info.me

    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
    relative_ball_position = (game_info.ball.pos - game_info.me.pos)
    ball_distance = relative_ball_position.magnitude()
    we_hit_ball = check_ball_contact(game_info, current_state)
    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 3500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 3500)
    if game_info.ball.pos.x > 0:
        ball_x_sign = 1
    else:
        ball_x_sign = -1
    on_net = game_info.ball_prediction.check_on_net()
        ############

    if not is_drivable_point(current_state.pos + current_state.rot.front.scalar_multiply(500)):
        plan.layers[0] = "Goal"
    elif we_hit_ball:
        #Once we touch the ball, go Recover.
        plan.layers[0] = "Recover"
    elif on_net[0] == -1:
        plan.layers[0] = "Ball"
    elif relative_ball_position.y < -250:
        #If we were going for the ball, but the ball is behind us, go for boost.
        plan.layers[0] = "Boost"
    elif ball_in_offensive_corner and game_info.me.boost < 60:
        #Don't attack the ball in their corner
        plan.layers[0] = "Boost"
    elif when_is_ball_shootable(current_state = current_state,
                                prediction = game_info.ball_prediction,
                                condition = is_ball_shootable)[0]:
        plan.layers[0] = "Ball"
    elif (ball_in_defensive_corner or ball_in_offensive_corner) and plan.old_plan[2] != "Aerial" and plan.old_plan[2] != "Path" and plan.old_plan[2] != "Hit ball" and ball_arrival == None: 
        #TODO: Wrap up all the checks into one 'mechanic lock'?
        plan.layers[0] = "Goal"
    elif plan.old_plan[2] == "Aerial" and game_info.game_time > 0.2 + persistent.aerial.target_time:
        #TODO: Add a check to see if another car touches the ball
        plan.layers[0] = "Recover"


    elif plan.path != None:
        plan.path_lock = True
        plan.layers[0] = "Ball"
    else:
        plan.layers[0] = "Ball"

    return plan, persistent

#######################################################################################################

def boost(plan, game_info, persistent):
    '''
    Decides when to break from "Boost" state.
    TODO: Time to get to boost and time saved by having boost.
    TODO: Time until the ball reaches our net?
    TODO: Time until opponent gets to ball
    TODO: Time until ball gets to a dangerous position
    '''

    current_state = game_info.me
    on_net = game_info.ball_prediction.check_on_net()
    if on_net[0] == -1:
        plan.layers[0] = "Ball"
    elif current_state.boost > 60:
        #If we were going for boost, but have enough boost, go to net.
        plan.layers[0] = "Goal"
    elif plan.path != None and plan.path.finished:
        #TODO: Will need to be updated once it starts doing things other than sitting in net.
        plan.layers[0] = "Goal"
    elif current_state.pos.y < -1000 and plan.path != None and plan.path.waypoints == [Vec3(0,-5120,0)]:
        #TODO: Check field info instead of hardcoding the goals everywhere?
        plan.layers[0] = "Goal"

    elif plan.path != None:
        plan.path_lock = True
        plan.layers[0] = "Boost"
    else:
        plan.layers[0] = "Boost"

    return plan, persistent

#######################################################################################################


def goal(plan, game_info, persistent):
    '''
    Decides when to break from "Goal" state.
    '''

    current_state = game_info.me

    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
    relative_ball_position = (game_info.ball.pos - game_info.me.pos)
    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 3500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 3500)
    target_pos = game_info.ball.pos

    if not is_drivable_point(current_state.pos + current_state.rot.front.scalar_multiply(500)):
        plan.layers[0] = "Goal"
    elif persistent.aerial.initialize:
        plan.layers[0] = "Ball"

    elif ball_arrival != None and ball_arrival[1].z < 150:
        plan.layers[0] = "Ball"
        plan.layers[1] = "Clear"
        plan.layers[2] = "Hit ball"

    elif when_is_ball_shootable(current_state = current_state,
                                prediction = game_info.ball_prediction,
                                condition = is_ball_shootable)[0]:
        plan.layers[0] = "Ball"

    elif ball_in_defensive_corner or ball_in_offensive_corner:
        plan.layers[0] = "Goal"

    elif plan.path != None:
        plan.path_lock = True
        plan.layers[0] = "Goal"
    else:
        plan.layers[0] = "Goal"

    return plan, persistent

#######################################################################################################


def recover(plan, game_info, persistent):
    '''
    Decides when to break from "Recover" state.
    '''

    current_state = game_info.me
    #have_steering_control = check_steering_control(game_info, current_state)
    enough_boost = current_state.boost > 60


    if plan.old_plan[1] == "Ground":# and have_steering_control: TODO: Get a better "have control" estimate.
        if not enough_boost:
            plan.layers[0] = "Boost"
        else:
            plan.layers[0] = "Goal"

    elif plan.path != None:
        plan.path_lock = True
        plan.layers[0] = "Recover"
    else:
        plan.layers[0] = "Recover"
    return plan, persistent


#######################################################################################################


def kickoff(plan, game_info, persistent):
    '''
    Decides what to do after hitting the ball on a kickoff.
    '''
    #TODO: This will need a lot of work in the near future.

    current_state = game_info.me

    #TODO: Add "score open net" functionality here, since we'll probably win
    #some kickoffs from time to time
    plan.layers[0] = "Boost"
    if current_state.vel.x > 0:
        plan.layers[1] = "Mid Boost+"
    else:
        plan.layers[1] = "Mid Boost-"

    return plan, persistent

###########################

###########################


def check_ball_contact(game_info, car_state):
    '''
    Returns a boolean for if the given car has hit the ball in the last frame.
    '''
    #TODO: Possibly update to compare indices instead

    if game_info.ball.latest_touch.player_index == game_info.my_index and game_info.game_time < game_info.ball.latest_touch.time_seconds + 1/20:
        return True
    else:
        return False


#Doesn't work, will need to be mostly or completely redone later.
def check_steering_control(game_info, car_state):
    '''
    A fairly naive check for if we have control of our steering after a recovery.
    Depends on the current steer input - it will not be entirely accurate for cars
    other than our own since we don't have that information, but we don't 
    need this function to be particularly accurate for other cars.
    '''

    if car_state != game_info.me:
        inputs = SimpleControllerState()
    else:
        inputs = game_info.inputs
    c1 = 0.2
    c2 = 0.5
    #Epsilons are large for now to make sure we don't miss it
    epsilon1 = 1
    epsilon2 = 1

    if car_state.wheel_contact:
        if abs(atan2(car_state.vel.y , car_state.vel.x) - inputs.steer * c1) < epsilon1:
            if abs(car_state.omega.z - inputs.steer * c2) < epsilon2:
                return True
    else:
        return False
