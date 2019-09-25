from math import atan2

from BallPrediction import get_ball_arrival, is_ball_in_front_of_net, is_ball_in_scorable_box
from CowBotVector import Vec3
from GameState import Orientation
from Pathing.WaypointPath import WaypointPath


def boost(plan, game_info, persistent):
    '''
    Once we've decided to go for boost, this function controls which boosts we go for.
    TODO: Update pad pathing and logic for when to go for big boosts.
    TODO: Get rid of the if/else for the ball position?
    '''

    current_state = game_info.me

    if game_info.ball.pos.x > 0:
        #Boost indices
        far_opp_boost = 29
        near_opp_boost = 30
        far_mid_boost = 15
        near_mid_boost = 18
        far_back_boost = 3
        near_back_boost = 4
    else:
        far_opp_boost = 30
        near_opp_boost = 29
        far_mid_boost = 18
        near_mid_boost = 15
        far_back_boost = 4
        near_back_boost = 3
  
    '''
    if current_state.pos.y > -2000 and game_info.boosts[far_mid_boost].is_active:
        plan.layers[1] = far_mid_boost
    elif game_info.boosts[far_back_boost].is_active:
        plan.layers[1] = far_back_boost
    elif game_info.ball.pos.y > 0 and game_info.boosts[near_back_boost].is_active:
        plan.layers[1] = near_back_boost
    else:
        #Break and go to goal, since we're not smart enough to get pads yet
        plan.layers[1] = "Pads"
        plan.path = WaypointPath(check_pads(game_info), current_state)
    '''

    plan.layers[1] = "Pads"
    if plan.path_lock:
        plan.path = WaypointPath(plan.path.waypoints, current_state)
    else:
        candidate_path = check_pads(game_info)
        if len(candidate_path) > 0:
            #This conditional is only needed if we might not pick a candidate path
            #Currently we pick the 'best' out of the options, even if it's not good
            #Eventually that is likely to change, although I suspect this code will
            #be significantly improved by time that happens
            plan.path = WaypointPath(candidate_path, current_state)
            plan.path_lock = True
        elif current_state.pos.y < -3000:
            plan.layers[0] = "Goal"
            plan.layers[1] = "Go to net"
        else:
            print("confusion?")
            #plan.path = WaypointPath([Vec3(0,-5120,0)], current_state)

    return plan, persistent

        
#######################################################################################################

def ball(plan, game_info, persistent):
    '''
    Once we've decided to go for the ball, this function controls how we're trying to hit the ball.
    '''

    current_state = game_info.me
    ball_distance = (game_info.ball.pos - current_state.pos).magnitude()
    #TODO: Make this better
    if game_info.ball.vel.magnitude() != 0 and current_state.vel.magnitude() != 0:        
        ball_car_dot = current_state.vel.normalize().dot(game_info.ball.vel.normalize())
    else:
        ball_car_dot = 0
        
    #########
        
    if ball_distance < 450 - 100*ball_car_dot and game_info.ball.pos.z < 200 and plan.old_plan[2] != "Aerial":
        #If we were going for the ball, and we're close to it, flip into it.
        plan.layers[1] = "Challenge"
    elif game_info.ball.pos.y > 0 and abs(game_info.ball.pos.x < 3000):
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
    '''
    Once we've decided to go to net, this function decides if we're going to net, staying in net, etc.
    '''

    current_state = game_info.me

    if game_info.ball.pos.x > 0:
        ball_x_sign = 1
    else:
        ball_x_sign = -1

    distance_to_net = (Vec3(0,-5120,15) - current_state.pos).magnitude()
    ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)

    #TODO: Update what counts as "corner"
    ball_in_defensive_corner = not (game_info.ball.pos.y > -1500 or abs(game_info.ball.pos.x) < 2500)
    ball_in_offensive_corner = not (game_info.ball.pos.y < 950 or abs(game_info.ball.pos.x) < 2500)

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
        #TODO: Adjust target orientation to be lined up with our landing, even on walls, etc.
        persistent.aerial_turn.target_orientation = Orientation(pyr = [0, atan2(current_state.vel.y, current_state.vel.x), 0])

    return plan, persistent




#######################################################################

#######################################################################

def check_pads(game_info):
    '''
    Decide which path of boost pads to go through, once we've decided to pick up pads.
    This is going to get ugly, and will probably warrant its own file eventually.
    '''

    current_state = game_info.me

    #A list of reasonable paths we might want to take
    #Doesn't take big pads into account for now
    boost_pads_path_list = [ [32, 28, 26, 20, 13, 7, 0], #top left to right mid to net
                             [32, 23, 21, 14, 11, 6, 0],     #top left to left mid to net
                             [33, 26, 20, 13, 7, 0],         #their net to center mid to net
                             [28, 23, 21, 14, 11, 6, 0],     #top left to left mid to net
                             [28, 26, 19, 12, 10, 5, 0],     #top left to right mid to net
                             [28, 20, 16, 10, 5, 0],         #top left to left-center mid to net
                             [28, 20, 13, 7, 0],
                             [26, 20, 13, 7, 0],             #top mid to center mid to net
                             [26, 21, 14, 11, 6, 0],         #top mid to left mid to net
                             [25, 21, 17, 13, 7, 0],         #top left to center mid to net
                             [25, 21, 14, 11, 6, 0],         #top left to left mid to net
                             [23, 21, 14, 11, 6, 0],         #top left to left mid to net
                             [23, 20, 16, 12, 10, 5, 0],     #top left to mid right to net041
                             [23, 20, 13, 7, 0],             #top left to center mid to net
                             [23, 17, 13, 7, 0],             #top left to left-center mid to net
                             [21, 14, 11, 6, 0],
                             [21, 17, 13, 7, 0],
                             [21, 17, 13, 5, 0],
                             [20, 13, 7, 0],
                             [20, 17, 14, 11, 6, 0],
                             [17, 14, 11, 6, 0],
                             [17, 13, 7, 0],
                             [14, 11, 6, 0],
                             [14, 7, 0],
                             [13, 7, 0],
                             [11, 6, 0],
                             [7, 0],
                             [6, 0] ]


    #Mirror all the paths above
    n = len(boost_pads_path_list)
    for index in range(n):
        boost_pads_path_list.append([ game_info.mirror_boost_list.index(boost_index) for boost_index in boost_pads_path_list[index] ])
    #TODO: Put this in initialization so it doesn't have to redo it every time we choose a path?
    product = 0
    best_path = []
    for path in boost_pads_path_list:
        first_segment = (game_info.boosts[path[1]].pos - game_info.boosts[path[0]].pos).normalize()
        first_boost = (game_info.boosts[path[0]].pos - current_state.pos).normalize()
        dot = first_segment.dot(first_boost)

        if dot < 0:
            continue
        elif dot > product:
            best_path = path
            product = dot


    #This is only useful if I'm picking paths based on ball position.
    #Since I'm only going by my position, this will ruin everything
    #if game_info.ball.pos.x <= 0:
    #index_list = [ game_info.mirror_boost_list.index(boost_index) for boost_index in index_list ]
        
    return [ game_info.boosts[boost_index].pos for boost_index in best_path ]




''' Here's a decent starting framework for team boost paths.  It's not great,
    and needs to take velocity and orientation into account, but is good enough for 
    until after the next 1v1 tournament. 


    boost_pads_path_list = [ [32, 28, 26, 19, 12, 10, 5, 0], #top left to right mid to net
                             [32, 28, 26, 19, 12, 10, 1],    #top left to right mid to right post
                             [32, 23, 21, 14, 11, 2],        #top left top left to left mid to left post
                             [32, 23, 21, 14, 11, 6, 0],     #top left to left mid to net
                             [33, 28, 23, 21, 14, 11, 6, 0], #their net to left mid to net
                             [33, 28, 23, 21, 14, 11, 2],    #their net to left mid to left post
                             [33, 26, 20, 13, 7, 0],         #their net to center mid to net
                             [33, 28, 23, 21, 17, 13, 10, 1], 
                             [33, 28, 23, 21, 17, 13, 10, 5, 0], 
                             [28, 23, 21, 14, 11, 2],        #top left to left mid to left post
                             [28, 23, 21, 14, 11, 6, 0],     #top left to left mid to net
                             [28, 26, 19, 12, 10, 5, 0],     #top left to right mid to net
                             [28, 26, 19, 12, 10, 1],        #top left to right mid to right post
                             [28, 20, 16, 12, 10, 1],        #top left to left-center mid to right post
                             [28, 20, 16, 12, 10, 5, 0],     #top left to left-center mid to net
                             [28, 20, 13, 7, 0],
                             [26, 20, 13, 7, 0],             #top mid to center mid to net
                             [26, 21, 14, 11, 6, 0],         #top mid to left mid to net
                             [26, 21, 14, 11, 2],            #top mid to left mid to left post
                             [25, 21, 17, 13, 10, 1],        #top left to center mid to right post
                             [25, 24, 17, 13, 7, 0],         #top left to center mid to net
                             [25, 24, 17, 13, 5, 0],         #top left to center mid to net
                             [25, 21, 14, 11, 6, 0],         #top left to left mid to net
                             [25, 21, 14, 11, 2],            #top left to left mid to left post
                             [23, 21, 14, 11, 2],            #top left to left mid to left post
                             [23, 21, 14, 11, 6, 0],         #top left to left mid to net
                             [23, 20, 16, 12, 10, 5, 0],     #top left to mid right to net041
                             [23, 20, 16, 12, 10, 1],        #top left to mid right to right post
                             [23, 20, 13, 7, 0],             #top left to center mid to net
                             [23, 17, 13, 7, 0],             #top left to left-center mid to net
                             [21, 14, 11, 2],                #etc.
                             [21, 14, 11, 6, 0],
                             [21, 17, 13, 7, 0],
                             [21, 17, 13, 10, 1],
                             [21, 17, 13, 5, 0],
                             [20, 13, 7, 0],
                             [20, 17, 14, 11, 6, 0],
                             [20, 17, 14, 11, 2],
                             [17, 14, 11, 6, 0],
                             [17, 14, 11, 2],
                             [17, 13, 7, 0],
                             [17, 13, 10, 1],
                             [17, 13, 5, 0],
                             [14, 11, 2],
                             [14, 11, 6, 0],
                             [14, 7, 5, 1],
                             [14, 7, 5, 0],
                             [13, 11, 6, 0],
                             [13, 11, 2],
                             [13, 6, 0],
                             [13, 7, 0],
                             [11, 7, 5, 1],
                             [11, 2],
                             [11, 6, 0],
                             [7, 0],
                             [7, 6, 0],
                             [7, 5, 0],
                             [6, 0 ],
                             [6, 2] ]

'''
