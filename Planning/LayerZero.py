from math import atan2

from BallPrediction import get_ball_arrival, is_ball_in_front_of_net, is_ball_in_scorable_box
from CowBotVector import Vec3

def ball(plan, game_info, persistent):
    current_state = game_info.me

    relative_ball_position = (game_info.ball.pos - game_info.me.pos)
    ball_distance = relative_ball_position.magnitude()
    we_hit_ball = check_ball_contact(game_info, current_state)
    teammate_is_back = False
    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)
    teammate_ball_distance = 100000
    teammate_distance_to_far_post = 100000
    if game_info.ball.pos.x > 0:
        ball_x_sign = 1
    else:
        ball_x_sign = -1

    for mate in game_info.teammates:
        if (mate.pos - game_info.ball.pos).magnitude() < teammate_ball_distance:
            teammate_ball_distance = (mate.pos - game_info.ball.pos).magnitude()
        if (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude() < teammate_distance_to_far_post:
            teammate_distance_to_far_post = (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude()

    for mate in game_info.teammates:
        if mate.pos.y < -2500:
            teammate_is_back = True

        ############

    if we_hit_ball:
        #Once we touch the ball, go Recover.
        plan.layers[0] = "Recover"
    elif relative_ball_position.y < -250:
        #If we were going for the ball, but the ball is behind us, go for boost.
        plan.layers[0] = "Boost"
    elif ball_in_offensive_corner and game_info.me.boost < 60:
        #Maybe try to center?
        plan.layers[0] = "Boost"
    elif (ball_in_defensive_corner or ball_in_offensive_corner) and plan.old_plan[2] != "Aerial" and plan.old_plan[2] != "Hit ball":
        #Check for teammates
        plan.layers[0] = "Goal"
    elif plan.old_plan[2] == "Aerial" and game_info.game_time > 0.3 + persistent.aerial.action.arrival_time:
        plan.layers[0] = "Recover"
    else:
        plan.layers[0] = "Ball"

    return plan, persistent

#######################################################################################################

def boost(plan, game_info, persistent):
    current_state = game_info.me
    #Path for small pads.  Don't loop for ten seconds on the big boost.
    if current_state.boost > 60:
        #If we were going for boost, but have enough boost, go to net.
        plan.layers[0] = "Goal"
    else:
        plan.layers[0] = "Boost"

    return plan, persistent

#######################################################################################################


def goal(plan, game_info, persistent):
    current_state = game_info.me

    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
    teammate_is_back = False
    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)

    for mate in game_info.teammates:
        if mate.pos.y < -2500:
            teammate_is_back = True


    if persistent.aerial.initialize:
        plan.layers[0] = "Ball"
    elif ball_arrival != None and ball_arrival[1].z < 200:
        plan.layers[0] = "Ball"
        plan.layers[1] = "Clear"
        plan.layers[2] = "Hit ball"
    elif game_info.team_mode != "1v1" and not teammate_is_back:
        plan.layers[0] = "Goal"
    elif game_info.team_mode != "1v1":
        if game_info.ball.pos.x > 0:
            plan.layers[0] = "Ball"
            plan.layers[1] = "Clear"
            plan.layers[2] = "Hit ball"
            for mate in game_info.teammates:
                if mate.pos.x > current_state.pos.x:
                    plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Ball"
            plan.layers[1] = "Clear"
            plan.layers[2] = "Hit ball"
            for mate in game_info.teammates:
                if mate.pos.x < current_state.pos.x:
                    plan.layers[0] = "Goal"

    elif is_ball_in_front_of_net(game_info.ball.pos) and game_info.team_mode == "1v1":
        #Predict when the ball will be in front of the net.
        plan.layers[0] = "Ball"
    elif ball_in_defensive_corner or ball_in_offensive_corner:
        plan.layers[0] = "Goal"
    else:
        plan.layers[0] = "Goal"

    return plan, persistent

#######################################################################################################


def recover(plan, game_info, persistent):
    current_state = game_info.me
    have_steering_control = check_steering_control(game_info, current_state)
    enough_boost = current_state.boost > 60


    if plan.old_plan[1] == "Ground":# and have_steering_control: This doesn't work as hoped yet.
        if not enough_boost:
            plan.layers[0] = "Boost"
        else:
            plan.layers[0] = "Goal"
    else:
        plan.layers[0] = "Recover"
    return plan, persistent

#######################################################################################################


def kickoff_pause(plan, game_info, persistent):
    current_state = game_info.me

    ball_distance = (game_info.ball.pos - current_state.pos).magnitude()
    if game_info.ball.pos.x > 0:
        ball_x_sign = 1
    else:
        ball_x_sign = -1

    teammate_ball_distance = 100000
    teammate_distance_to_far_post = 100000
    for mate in game_info.teammates:
        if (mate.pos - game_info.ball.pos).magnitude() < teammate_ball_distance:
            teammate_ball_distance = (mate.pos - game_info.ball.pos).magnitude()
        if (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude() < teammate_distance_to_far_post:
            teammate_distance_to_far_post = (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude()


    #If it's a kickoff, and we're strictly the closest on our team, run Kickoff code.
    #If someone is at least as close as us, go get boost.
    #Wait a split second (if same distance), and if they leave, go for ball
    if len(game_info.teammates) > 0 and teammate_ball_distance > ball_distance - 50 and current_state.pos.x > 0:
        #left goes :(
        plan.layers[0] = "Kickoff"
    elif len(game_info.teammates) > 0 and teammate_ball_distance < ball_distance + 50:
        #TODO: Check if teammate is taking a boost, if they are, go for the other one
        plan.layers[0] = "Boost"
    else:
        plan.layers[0] = "Kickoff"

    return plan, persistent

#######################################################################################################


def kickoff(plan, game_info, persistent):
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

    if game_info.ball.latest_touch.player_name == game_info.my_name and game_info.game_time < game_info.ball.latest_touch.time_seconds + 1/20:
        return True
    else:
        return False



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
