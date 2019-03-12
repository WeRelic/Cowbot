from Mechanics import *
from Maneuvers import *


def far_back(game_info, old_game_info, opponent_distance, team_sign, controller_input):
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)



    #Set which boost we want based on team.
    if team_sign == 1:
        first_boost = 7
    else:
        first_boost = 26

    if abs(current_state.pos.y) > 4000:
        #Boost to start
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos)).input()
                                      
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 3817:
        #Turn to line up the dodge
        controller_input = QuickTurn(1, True).input()


    elif abs(current_state.pos.y) > 2500 and current_state.wheel_contact:
        #Jump to prep for the dodge
        controller_input.jump = 1

    elif abs(current_state.pos.y) > 3400:
        #If we're far away, fast dodge to speed up
        controller_input = CancelledFastDodge(current_state, -1).input()

    elif abs(current_state.pos.y) < 400:# and opponent_distance < 1000:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1, 0, 0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and abs(current_state.pos.y) < 1000:# and opponent_distance < 1000:
        #If we're on the ground, close, and the opponent is also close,
        #jump and turn towards the ball to prep for the dodge.
        if current_state.yaw > ball_angle:
            direction = -1
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif abs(current_state.pos.y) < 375:
        #If the opponent is far away and we're close to the ball, take a single jump shot
        controller_input.jump = 1

    elif current_state.wheel_contact:
        #Otherwise if we're on the ground, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        controller_input.boost = 1
        
    else:
        #Otherwise turn towards the ball (this might not actually do anything)
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()

    return controller_input


#########################################################################################################

#########################################################################################################


def offcenter(game_info, old_game_info, opponent_distance, team_sign, x_sign, controller_input):
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    #Offset added to the ball position for our initial steer
    offset = Vec3(x_sign*team_sign*625,0,0)

    #Set which boost we want based on team.
    if team_sign == 1:
        first_boost = 7
    else:
        first_boost = 26
        
    if abs(current_state.pos.x) > 80 and abs(current_state.pos.y) > 950:
        #If we're not near the center-line of the field, boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos+offset)).input()
        controller_input.boost = 1


    elif abs(current_state.pos.y) > 700 and current_state.pos.z < 110:
        controller_input.jump = 1
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 700:
        #If we're far away, fast dodge to speed up.
        controller_input = CancelledFastDodge(current_state, x_sign).input()

    else:
        controller_input = AerialRotation(current_state,
                                          current_state.copy_state(roll = 0),
                                          old_state).input()
        controller_input.boost = 1


    return controller_input



#########################################################################################################

#########################################################################################################


def diagonal(game_info, old_game_info,opponent_distance, team_sign, x_sign, controller_input):
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(x_sign*team_sign*750,0,0)

    #Set which boost we want based on team and side.
    if team_sign == 1:
        if x_sign == -1:
            first_boost = 11
        else:
            first_boost = 10
    else:
        if x_sign == -1:
            first_boost = 22
        else:
            first_boost = 23


    if abs(current_state.pos.y) > 2000:
        #If we haven't taken the small boost yet, drive towards it
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos + offset)).input()
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 1100 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 1100 and current_state.pos.z < 85:
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 500:
        #If we've taken the boost but are still far away, fast dodge to speed up
        controller_input = CancelledFastDodge(current_state, x_sign).input()

    else:
        controller_input = AerialRotation(current_state,
                                          current_state.copy_state(roll = 0),
                                          old_state).input()
        controller_input.boost = 1
        
    return controller_input
