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
        Challenege
        Save
        Clear
        Shot
        Corner
    Boost:
        Boost+
        Boost-; these will be deprecated for small pad pathing in the near future.
    Flip into Ball
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

    if len(game_info.teammates) > 0:
        first_teammate_pos = game_info.teammates[0].pos

    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)

    #2 is just the time I picked, it can (and should) be picked more intelligently.
    shot_on_goal = check_on_goal(ball_prediction, game_info.game_time + 2)

    #Very rough opponent distance estimator.  TODO: Improve.
    opponent_is_close = (game_info.opponents[0].pos - game_info.ball.pos).magnitude() > 200

    #######################################################################
    #Layer 0
    #######################################################################

    if game_info.is_kickoff_pause:
        #If it's a kickoff, and we're strictly the closest on our team, run Kickoff code.
        #If someone is at least as close as us, go get boost.
        if len(game_info.teammates) > 0 and first_teammate_pos.magnitude() < ball_distance + 50:
            plan.layers[0] = "Boost"
        else:
            plan.layers[0] = "Kickoff"

    elif old_plan[0] == "Kickoff":
        #TODO: Add "score open net" functionality here, since we'll probably win
        #some kickoffs from time to time
        plan.layers[0] = "Boost"


        #######################################################################

    elif old_plan[0] == "Ball":
        if last_touch.team == my_team and dist_from_last_touch < 200:
            #Once we touch the ball, go Recover. TODO: Update this to be better.
            plan.layers[0] = "Recover"
        elif relative_ball_position < -250:
            #If we were going for the ball, but the ball is behind us, go for boost.
            plan.layers[0] = "Boost"
        elif ball_in_offensive_corner and game_info.me.boost < 60:
            plan.layers[0] = "Boost"
        elif (ball_in_defensive_corner or ball_in_offensive_corner) and old_plan[2] != "Aerial":
            plan.layers[0] = "Goal"
        #elif old_plan[2] == "Aerial" and game_info.game_time > persistent.aerial.action.arrival_time + 1/30:
        #    plan.layers[0] = "Recover"
        else:
            plan.layers[0] = "Ball"


        #######################################################################

    elif old_plan[0] == "Boost":
        if current_state.boost > 60:
            #If we were going for boost, but have enough boost, go to net.
            plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Boost"

        #######################################################################
        
    elif old_plan[0] == "Goal":
        if persistent.aerial.initialize:
            plan.layers[0] = "Ball"
        elif is_ball_in_front_of_net(game_info.ball.pos):
            plan.layers[0] = "Ball"
        elif ball_in_defensive_corner or ball_in_offensive_corner:
            plan.layers[0] = "Goal"
        else:
            plan.layers[0] = "Goal"

    #######################################################################
    #Layer 1
    #######################################################################


    if plan.layers[0] == "Boost":
        if game_info.ball.pos.x > 0:
            plan.layers[1] = "Boost-"
        else:
            plan.layers[1] = "Boost+"

    #######################################################################     
    elif plan.layers[0] == "Ball":
        if ball_distance < 450 - 100*ball_car_dot and game_info.ball.pos.z < 250 and old_plan[2] != "Aerial":
            #If we were going for the ball, and we're close to it, flip into it.
            plan.layers[1] = "Flip into Ball"
        elif shot_on_goal:
            plan.layers[1] = "Save"
        elif game_info.ball.pos.y > 0 and is_ball_in_front_of_net(game_info.ball.pos):
            plan.layers[1] = "Shot"
        else:
            plan.layers[1] = "Clear"

    #######################################################################
    elif plan.layers[0] == "Kickoff":
        pass

    #######################################################################
    elif plan.layers[0] == "Goal":
        if current_state.wheel_contact and distance_to_net > 500:
            plan.layers[1] = "Go to net"
        
        elif ball_in_defensive_corner or ball_in_offensive_corner:
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
    #######################################################################

    if plan.layers[0] == "Ball":
        if persistent.aerial.initialize:
            plan.layers[2] = "Aerial"
        elif old_plan[2] == "Aerial":
            plan.layers[2] = "Aerial"
        elif plan.layers[1] == "Save":
            if game_info.ball.vel.magnitude() != 0 and (Vec3(cos(current_state.rot.yaw) , sin(current_state.rot.yaw), 0)).dot((game_info.ball.vel).normalize()) < - pi/8:
                plan.layers[2] = "Backwards"
            

    if plan.layers[0] == "Goal":
        if game_info.ball.pos.y < -4000 and get_ball_arrival(game_info, is_ball_in_front_of_net) != None:
            plan.layers[1] = "Wait"
            plan.layers[2] = "Prep for Aerial"

    #######################################################################

    #Reset any flags that might've been called previously.
    persistent.aerial.initialize = False


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
        if abs(pred.slices[i].pos.y) > 5120+92.75:
            on_net = True
            break

        i +=1
    return on_net
















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
