from math import atan2

from BallPrediction import PredictionPath, check_on_goal, get_ball_arrival, is_ball_in_front_of_net, is_ball_in_scorable_box
from CowBotVector import Vec3
from GameState import Orientation
from Miscellaneous import check_in_net, check_far_post, predict_for_time
from Pathing.WaypointPath import WaypointPath




def boost(plan, game_info, persistent):
    current_state = game_info.me

    if not game_info.is_kickoff_pause:
        if game_info.ball.pos.x > 0:
            #Boost indices
            far_opp_boost = 29
            near_opp_boost = 30
            far_mid_boost = 15
            near_mid_boost = 18
            far_back_boost = 3
            near_back_boost = 4
            if game_info.boosts[far_mid_boost].is_active:
                plan.layers[1] = "Mid Boost-"
            elif game_info.boosts[far_back_boost].is_active:
                plan.layers[1] = "Back Boost-"
            elif game_info.ball.pos.y > 0 and game_info.boosts[near_back_boost].is_active:
                plan.layers[1] = "Back Boost+"
            else:
                #Break and go to goal, since we're not smart enough to get pads yet
                plan.layers[1] = "Pads"
                path = WaypointPath(check_pads(game_info), current_state)

        else:
            far_opp_boost = 30
            near_opp_boost = 29
            far_mid_boost = 18
            near_mid_boost = 15
            far_back_boost = 4
            near_back_boost = 3

            if current_state.pos.y > -2000 and game_info.boosts[far_mid_boost].is_active:
                plan.layers[1] = "Mid Boost+"
            elif game_info.boosts[far_back_boost].is_active:
                plan.layers[1] = "Back Boost+"
            elif game_info.ball.pos.y > 0 and game_info.boosts[near_back_boost].is_active:
                plan.layers[1] = "Back Boost-"
            else:
                #Break and go to goal, since we're not smart enough to get pads yet
                plan.layers[1] = "Pads"
                path = WaypointPath(check_pads(game_info), current_state)

    else:
        if current_state.pos.x < 0:
            plan.layers[1] = "Back Boost-"
        elif current_state.pos.x > 0:
            plan.layers[1] = "Back Boost+"
        else:
            #If we're all the way back, check what teammate does
            plan.layers[1] = "Back Boost-"

    return plan, persistent

        
#######################################################################################################

def ball(plan, game_info, persistent):
    current_state = game_info.me

    ball_distance = (game_info.ball.pos - current_state.pos).magnitude()
    #2 is just the time I picked, it can (and should) be picked more intelligently.
    ball_prediction = PredictionPath(game_info.utils_game, predict_for_time(2))
    shot_on_goal = check_on_goal(ball_prediction, game_info.game_time + 2)
    
    #TODO: Make this better
    if game_info.ball.vel.magnitude() != 0 and current_state.vel.magnitude() != 0:        
        ball_car_dot = current_state.vel.normalize().dot(game_info.ball.vel.normalize())
    else:
        ball_car_dot = 0
        
    #########
        
    if ball_distance < 450 - 100*ball_car_dot and game_info.ball.pos.z < 250 and plan.old_plan[2] != "Aerial":
        #If we were going for the ball, and we're close to it, flip into it.
        plan.layers[1] = "Challenge"
    elif game_info.ball.pos.y > 0 and is_ball_in_front_of_net(game_info.ball.pos):
        #TODO: Predict when it'll get there
        plan.layers[1] = "Shot"
    else:
        plan.layers[1] = "Clear"
        
    return plan, persistent

#######################################################################################################

def kickoff(plan, game_info, persistent):
    return plan, persistent



#######################################################################################################

def goal(plan, game_info, persistent):
    current_state = game_info.me

    teammate_in_net = False
    teammate_far_post = False
    if game_info.ball.pos.x > 0:
        ball_x_sign = 1
    else:
        ball_x_sign = -1
        
    for mate in game_info.teammates:
        if check_in_net(mate.pos):
            teammate_in_net = True
        if check_far_post(mate.pos, ball_x_sign):
            teammate_far_post = True

    distance_to_net = (Vec3(0,-5120,15) - current_state.pos).magnitude()
    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
    
    if current_state.pos.x > 0:
        distance_to_far_boost = (current_state.pos - game_info.boosts[3].pos).magnitude()
        distance_to_far_post = (current_state.pos - Vec3(-1150, -5120+80, 0)).magnitude()
    else:
        distance_to_far_boost = (current_state.pos - game_info.boosts[4].pos).magnitude()
        distance_to_far_post = (current_state.pos - Vec3(1150, -5120+80, 0)).magnitude()

    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 1500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 1500)
    teammate_ball_distance = 100000
    teammate_distance_to_far_post = 100000

    for mate in game_info.teammates:
        if (mate.pos - game_info.ball.pos).magnitude() < teammate_ball_distance:
            teammate_ball_distance = (mate.pos - game_info.ball.pos).magnitude()
        if (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude() < teammate_distance_to_far_post:
            teammate_distance_to_far_post = (mate.pos - Vec3(-ball_x_sign*1150,-5120+80,0)).magnitude()


    #Wait far post instead sometimes
    if distance_to_net > 500:
        plan.layers[1] = "Go to net"
    elif ball_in_defensive_corner or ball_in_offensive_corner:
        plan.layers[1] = "Wait in net"
    else:
        plan.layers[1] = "Wait in net"
    return plan, persistent

        
        #######################################################################

def recover(plan, game_info, persistent):
    current_state = game_info.me

    if current_state.wheel_contact:
        plan.layers[1] = "Ground"
    else:
        plan.layers[1] = "Air"
        persistent.aerial_turn.initialize = True
        #This is a default value, but is the best I can do for the time being.  Recoveries will be updated in the future.
        persistent.aerial_turn.target_orientation = Orientation(pyr = [0, atan2(current_state.vel.y, current_state.vel.x), 0])
    return plan, persistent




#######################################################################

#######################################################################

def check_pads(game_info):
    current_state = game_info.me

    if game_info.ball.pos.x > 0:
        if current_state.pos.y > 2816:
            if current_state.pos.x > 2048:
                index_list = [23, 20, 16, 12, 10, 1]
            elif current_state.pos.x > 100:
                index_list = [20, 16, 12, 10, 1]
            else:
                index_list = [22, 19, 12, 10, 1]
                
            #######

        elif current_state.pos.y > 1024 + 100:
            if current_state.pos.x > 2048 + 100:
                index_list = [21, 17, 13, 10, 1]
            elif current_state.pos.x > 100:
                index_list = [20, 16, 12, 10, 1]
            else:
                index_list = [19, 12, 10, 1]

            #######
            
        elif current_state.pos.y > 100:
            if current_state.pos.x > 1024 + 100:
                index_list = [17, 13, 10, 1]
            elif current_state.pos.x > -1024 + 100:
                index_list = [16, 12, 10, 1]
            else:
                index_list = [12, 10, 1]

            #######

        elif current_state.pos.y > -2300 + 100:
            if current_state.pos.x > 2048 + 100:
                index_list = [14, 13, 12, 10, 1]
            elif current_state.pos.x > 100:
                index_list = [13, 12, 10, 1]
            else:
                index_list = [12, 10, 1]

            #######

        else:
            if current_state.pos.x > 1788 + 100:
                index_list = [11, 13, 12, 10, 1]
            elif current_state.pos.x > -1788 + 100:
                index_list = [7, 13, 12, 10, 1]
            else:
                index_list = [8, 12, 10, 1]


        ##############################################################

        ##############################################################

    elif game_info.ball.pos.x <= 0:
        if current_state.pos.y > 2816:
            if current_state.pos.x < -2048:
                index_list = [22, 20, 17, 14, 11, 2]
            elif current_state.pos.x < -100:
                index_list = [20, 17, 14, 11, 2]
            else:
                index_list = [23, 21, 14, 11, 2]
                
            #######

        elif current_state.pos.y > 1024 + 100:
            if current_state.pos.x < -2048 - 100:
                index_list = [19, 16, 13, 11, 2]
            elif current_state.pos.x < -100:
                index_list = [20, 17, 14, 11, 2]
            else:
                index_list = [21, 14, 11, 2]

            #######
            
        elif current_state.pos.y > 100:
            if current_state.pos.x < -1024 - 100:
                index_list = [16, 13, 11, 2]
            elif current_state.pos.x < 1024 - 100:
                index_list = [17, 14, 11, 2]
            else:
                index_list = [14, 11, 2]

            #######

        elif current_state.pos.y > -2300 + 100:
            if current_state.pos.x < -2048 - 100:
                index_list = [12, 13, 14, 11, 2]
            elif current_state.pos.x < -100:
                index_list = [13, 14, 11, 2]
            else:
                index_list = [14, 11, 2]

            #######

        else:
            if current_state.pos.x < -1788 - 100:
                index_list = [10, 13, 14, 11, 2]
            elif current_state.pos.x < 1788 - 100:
                index_list = [7, 13, 14, 11, 2]
            else:
                index_list = [9, 14, 11, 2]


    return [ game_info.boosts[boost_index].pos for boost_index in index_list ]
