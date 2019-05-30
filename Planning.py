from BallPrediction import *
from CowBotVector import *
from GamePlan import GamePlan
import Miscellaneous

def make_plan(game_info, old_plan, persistent):

    '''
    The function that is currently handling decision making.  This will need to 
    split as it grows and becomes more complicated.  Takes in the plan from the previous 
    frame and the current game state and makes a new plan decision.
    Possible top-level plan states are:
    Kickoff
    Ball:
        Save
        Clear
        Shot
        Challenge
    Boost:
        Back Boost+
        Back Boost-
        Mid Boost+
        Mid Boost-
    Goal:
        Go to net
        Wait
        Far post
        Prep for Aerial
    Recover:
        Ground
        Air
    '''
    
    #Some quantities that are used in decision making.

    plan = GamePlan()
    plan.old_plan = old_plan
    current_state = game_info.me
    ball_prediction = PredictionPath(game_info.utils_game, Miscellaneous.predict_for_time(2))
    if game_info.ball.vel.magnitude() != 0 and current_state.vel.magnitude() != 0:
        normalized_ball_vel = game_info.ball.vel.normalize()
        normalized_car_vel = current_state.vel.normalize()
        ball_car_dot = normalized_car_vel.dot(normalized_ball_vel)
    else:
        ball_car_dot = 0
    relative_ball_position = (game_info.ball.pos.y - game_info.me.pos.y)
    dist_from_last_touch = (game_info.ball.hit_location - game_info.me.pos).magnitude()
    last_touch = game_info.ball.last_touch
    my_team = game_info.my_team
    ball_distance = (game_info.ball.pos - current_state.pos).magnitude()
    distance_to_net = (Vec3(0,-5120,15) - current_state.pos).magnitude()
    we_hit_ball = check_ball_contact(game_info, current_state)
    have_steering_control = check_steering_control(game_info, current_state)
    team_mode = check_team_mode(game_info)
    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)

    if len(game_info.teammates) > 0:
        first_teammate_pos = game_info.teammates[0].pos
    if len(game_info.teammates) > 1:
        second_teammate_pos = game_info.teammates[1].pos

    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)

    #2 is just the time I picked, it can (and should) be picked more intelligently.
    shot_on_goal = check_on_goal(ball_prediction, game_info.game_time + 2)

    #Very rough opponent distance estimator.  TODO: Improve.
    for opp in game_info.opponents:
        if (game_info.opponents[0].pos - game_info.ball.pos).magnitude() < 200:
            opponent_is_close = True
            break
        else: opponent_is_close = False
    teammate_ball_distance = 100000
    for mate in game_info.teammates:
        if (mate.pos - game_info.ball.pos).magnitude() < teammate_ball_distance:
            teammate_ball_distance = (mate.pos - game_info.ball.pos).magnitude()


    #######################################################################
    #Layer 0
    #######################################################################

    if game_info.is_kickoff_pause:
        #If it's a kickoff, and we're strictly the closest on our team, run Kickoff code.
        #If someone is at least as close as us, go get boost.
        #Wait a split second (if same distance), and if they leave, go for ball
        if len(game_info.teammates) > 0 and teammate_ball_distance < ball_distance + 50:
            #TODO: Check if teammate is taking a boost, if they are, go for the other one
            plan.layers[0] = "Boost"
        else:
            plan.layers[0] = "Kickoff"

    elif old_plan[0] == "Kickoff":
        #TODO: Add "score open net" functionality here, since we'll probably win
        #some kickoffs from time to time
        plan.layers[0] = "Boost"
        if current_state.vel.x > 0:
            plan.layers[1] = "Mid Boost+"
        else:
            plan.layers[1] = "Mid Boost-"

        #######################################################################

    elif old_plan[0] == "Ball":
        if we_hit_ball:
            #Once we touch the ball, go Recover.
            plan.layers[0] = "Recover"
        elif relative_ball_position < -250:
            #If we were going for the ball, but the ball is behind us, go for boost.
            plan.layers[0] = "Boost"
        elif ball_in_offensive_corner and game_info.me.boost < 60:
            #Maybe try to center?
            plan.layers[0] = "Boost"
        elif (ball_in_defensive_corner or ball_in_offensive_corner) and old_plan[2] != "Aerial" and old_plan[2] != "Hit ball":
            #Check for teammates
            plan.layers[0] = "Goal"
        elif old_plan[2] == "Aerial" and game_info.game_time > 0.3 + persistent.aerial.action.arrival_time:
            plan.layers[0] = "Recover"
        else:
            plan.layers[0] = "Ball"

        #######################################################################

    elif old_plan[0] == "Boost":
        #Path for small pads.  Don't loop for ten seconds on the big boost.
        if current_state.boost > 60:
            #If we were going for boost, but have enough boost, go to net.
            plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Boost"

        #######################################################################

    elif old_plan[0] == "Goal":
        if persistent.aerial.initialize:
            plan.layers[0] = "Ball"
        elif ball_arrival != None and ball_arrival[1].z < 200:
            plan.layers[0] = "Ball"
            plan.layers[1] = "Clear"
            plan.layers[2] = "Hit ball"
        elif team_mode != "1v1":
            plan.layers[0] = "Goal"
        elif is_ball_in_front_of_net(game_info.ball.pos) and team_mode == "1v1":
            #Predict when the ball will be in front of the net.
            plan.layers[0] = "Ball"
        elif ball_in_defensive_corner or ball_in_offensive_corner:
            plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Goal"

    elif old_plan[0] == "Recover":
        if old_plan[1] == "Ground" and have_steering_control:
            if current_state.boost < 60:
                plan.layers[0] = "Boost"
            else:
                plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Recover"

    #######################################################################
    #Layer 1
    #######################################################################

    if plan.layers[0] == "Boost" and plan.layers[1] == None:
        if not game_info.is_kickoff_pause:
            if game_info.ball.pos.x > 0 :
                plan.layers[1] = "Back Boost-"
            else:
                plan.layers[1] = "Back Boost+"
        else:
            if current_state.pos.x < 0:
                plan.layers[1] = "Back Boost-"
            elif current_state.pos.x > 0:
                plan.layers[1] = "Back Boost+"
            else:
                #If we're all the way back, check what teammate does
                plan.layers[1] = "Back Boost-"

    #######################################################################     
    elif plan.layers[0] == "Ball":
        if ball_distance < 450 - 100*ball_car_dot and game_info.ball.pos.z < 250 and old_plan[2] != "Aerial":
            #If we were going for the ball, and we're close to it, flip into it.
            plan.layers[1] = "Challenge"
        #elif shot_on_goal: #We'll make this do things later.
            #plan.layers[1] = "Save"
        elif game_info.ball.pos.y > 0 and is_ball_in_front_of_net(game_info.ball.pos) and team_mode == "1v1":
            #Predict when it'll get there
            plan.layers[1] = "Shot"
        else:
            plan.layers[1] = "Clear"

    #######################################################################
    elif plan.layers[0] == "Kickoff":
        pass

    #######################################################################
    elif plan.layers[0] == "Goal":
        #Wait far post instead sometimes
        if distance_to_net > 500:
            plan.layers[1] = "Go to net"
        elif ball_in_defensive_corner or ball_in_offensive_corner:
            plan.layers[1] = "Wait"
        elif ball_arrival != None:
            if ball_arrival[1].z > 200:
                plan.layers[1] = "Wait"
        else:
            plan.layers[1] = "Wait"

    #######################################################################
    elif plan.layers[0] == "Recover":
        if current_state.wheel_contact:
            plan.layers[1] = "Ground"
        else:
            plan.layers[1] = "Air"


    #######################################################################
    #Layer 2
    ###############k########################################################

    if plan.layers[0] == "Ball":
        if persistent.aerial.initialize:
            plan.layers[2] = "Aerial"
        elif old_plan[2] == "Aerial":
            plan.layers[2] = "Aerial"
        elif plan.layers[1] == "Save":
            pass
            #if game_info.ball.vel.magnitude() != 0 and (Vec3(cos(current_state.rot.yaw) , sin(current_state.rot.yaw), 0)).dot((game_info.ball.vel).normalize()) > pi/8:
                #plan.layers[2] = "Backwards"
        elif old_plan[2] == "Hit ball":
            plan.layers[2] = "Hit ball"

    if plan.layers[0] == "Goal":
        if ball_arrival != None:
            if ball_arrival[1].z > 200:
                plan.layers[2] = "Prep for Aerial"


    #######################################################################

    #Reset any flags that might've been called previously.
    persistent.aerial.initialize = False
    persistent.hit_ball.initialize = False


    #Get ready for next frame, and return
    print(plan.layers, plan.old_plan)
    plan.old_plan = plan.layers
    #Return our final decision
    return plan

#######################################################################
#Helper functions
#######################################################################


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


###########################


def check_ball_contact(game_info, car_state):
    '''
    Returns a boolean for if the given car has hit the ball in the last frame.
    '''

    if (car_state.pos - game_info.ball.pos).magnitude() < 200:
        return True
    else:
        return False


###########################


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


###########################

def check_team_mode(game_info):
    if len(game_info.teammates) == 0:
        return "1v1"
    elif len(game_info.teammates) == 1:
        return "2v2"
    elif len(game_info.teammates) == 2:
        return "3v3"
    else:
        return "Other"






#TODO: Add time estimates for getting to the ball, and predicting when it'll roll into the center of the field.  This will let us take shots more reliably, since we'll be getting there _before_ it rolls out of reach.

















''' Old 2v2 code.  Probably not worth much, but it belongs here instead of in Cowculate anyway.

    elif len(game_info.teammates) > 0:
        #Team code, likely very bad
        ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
        teammate_in_net = abs(game_info.teammates[0].pos.x) < 900 and game_info.teammates[0].pos.y < -4700

        if game_info.ball.pos.y > -1500:
            #Don't go into the opponents' half
            controller_input, persistent = wait_in_net(game_info, persistent)
        elif teammate_in_net and not shot_on_goal:
            #Don't cut off teammate unless you need to make a save
            controller_input, persistent = wait_far_post(game_info, persistent)
        elif ball_in_defensive_corner:
            #Wait in net if the ball is in the corner and teammate isn't in net
            controller_input, persistent = wait_in_net(game_info, persistent)
        else:
            controller_input, persistent = go_for_ball(game_info, shot_on_goal, persistent)

    else:
        #If it's a 1v1, go for the ball next
        #Turn towards ball, and boost if on the ground and not supersonic.
        controller_input = GroundTurn(current_state, current_state.copy_state(pos = game_info.ball.pos)).input()
        if current_state.vel.magnitude() < 2250 and current_state.wheel_contact:
            controller_input.boost = 1
'''
