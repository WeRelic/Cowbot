from Maneuvers import *
from Mechanics import *


def far_back(game_info, old_game_info, opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    if abs(current_state.pos.y) > 3000:
        #If we're far away, fast dodge to speed up
        controller_input = FastDodge(current_state,
                                     current_state.copy_state(pos = Vec3(-250,0,0)),
                                     old_state,
                                     boost_threshold = 1250,
                                     direction = -1).input()

    elif abs(current_state.pos.y) < 400 and opponent_distance < 1000:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and abs(current_state.pos.y) < 1000 and abs(game_info.opponents[0].pos.y) < 1000:
        #If we're on the ground, close, and the opponent is also close,
        #jump and turn towards the ball to prep for the dodge.
        if current_state.rot.yaw > ball_angle:
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


def back_left(game_info, old_game_info, opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Set which boost we want based on team.
    if game_info.team_sign == 1:
        first_boost = 7
    else:
        first_boost = 26

    if abs(current_state.pos.x) > 80 and abs(current_state.pos.y) > 3200:
        #If we're not near the center-line of the field, boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.boosts[first_boost].pos+Vec3(0,200,0))).input()
        controller_input.boost = 1
            
    elif abs(current_state.pos.y) > 1200:
        #If we're far away, fast dodge to speed up.
        controller_input = FastDodge(current_state,
                                     current_state.copy_state(pos = Vec3(-450,0,0)),
                                     old_state,
                                     oversteer = False,
                                     boost_threshold = 1200,
                                     direction = -1).input()

    elif abs(current_state.pos.y) < 350 and opponent_distance < 1000:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and (current_state.vel.magnitude() > 2000) and abs(game_info.opponents[0].pos.y) < 1000:
        #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = 0
        else:
            direction = 1
        controller_input = JumpTurn(current_state, -1, direction).input()
    elif abs(current_state.pos.y) < 350:
        #If we're close and the opponent isn't, single jump to shoot on net
        controller_input.jump = 1
    elif current_state.wheel_contact:
        #If we're on the ground between stages, boost and turn towards the ball
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


def back_right(game_info, old_game_info, opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Set which boost we want based on team.
    if game_info.team_sign == 1:
        first_boost = 7
    else:
        first_boost = 26
        
    if abs(current_state.pos.x) > 80 and abs(current_state.pos.y) > 3200:
        #If we're not near the center-line of the field, boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.boosts[first_boost].pos+Vec3(0,200,0))).input()
        controller_input.boost = 1
            
    elif abs(current_state.pos.y) > 1200:
        #If we're far away, fast dodge to speed up.
        controller_input = FastDodge(current_state,
                                     current_state.copy_state(pos = Vec3(450 * 0,0)),
                                     old_state,
                                     oversteer = False,
                                     boost_threshold = 1200,
                                     direction = 1).input()
            
    elif abs(current_state.pos.y) < 350 and opponent_distance < 1000:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and (current_state.vel.magnitude() > 2000) and opponent_distance < 1000:
        #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = -1
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()
    elif abs(current_state.pos.y) < 350:
        #If we're close and the opponent isn't, single jump to shoot on net
        controller_input.jump = 1
    elif current_state.wheel_contact:
        #If we're on the ground between stages, boost and turn towards the ball
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


def left(game_info, old_game_info,opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Set which boost we want based on team.
    if game_info.team_sign == 1:
        first_boost = 11
    else:
        first_boost = 22

    if game_info.boosts[first_boost].is_active:
        #If we haven't taken the small boost yet, drive towards it
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.boosts[first_boost].pos + Vec3(125,0,0))).input()
        controller_input.boost = 1


    elif abs(current_state.pos.y) > 1200:
        #If we've taken the boost but are still far away, fast dodge to speed up
        controller_input = FastDodge(current_state,
                                     current_state.copy_state(pos = Vec3(500,0,0)),
                                     old_state,
                                     boost_threshold = 1000,
                                     direction = -1).input()

    elif current_state.double_jumped:
        #Once we dodge, turn towards the ball in the air.
        controller_input.yaw = -1

    elif abs(current_state.pos.y) < 250 and opponent_distance < 1000:
        #If both players are close to the ball, dodge into the ball.
        controller_input = AirDodge(Vec3(1/sqrt(2),-1/sqrt(2),0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and (current_state.vel.magnitude() > 1725) and opponent_distance < 1000:
        #If we're approaching the ball and the opponent is close,
        #jump turn into ball to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = 0
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif abs(current_state.pos.y) < 350:
        #If we're close to the ball and the opponent is far away, take a single jump shot.
        controller_input.jump = 1

    elif current_state.wheel_contact:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        controller_input.boost = 1

    return controller_input

#########################################################################################################

#########################################################################################################

def right(game_info, old_game_info, opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    #Set which boost we want based on team.
    if game_info.team_sign == 1:
        first_boost = 10
    else:
        first_boost = 23
            
    if game_info.boosts[first_boost].is_active:
        #If we haven't taken the small boost yet, drive towards it
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.boosts[first_boost].pos + Vec3(125,0,0))).input()
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 1200:
        #If we've taken the boost but are still far away, fast dodge to speed up
        controller_input = FastDodge(current_state,
                                     current_state.copy_state(pos = Vec3(500,0,0)),
                                     old_state,
                                     boost_threshold = 1000,
                                     direction = 1).input()

    elif current_state.double_jumped:
        #Once we dodge, turn towards the ball in the air.
        controller_input.yaw = 1

    elif abs(current_state.pos.y) < 250 and opponent_distance < 1000:
        #If both players are close to the ball, dodge into the ball.
        controller_input = AirDodge(Vec3(1/sqrt(2),1/sqrt(2),0),
                                    current_state.jumped_last_frame).input()
        
    elif current_state.wheel_contact and (current_state.vel.magnitude() > 1725) and opponent_distance < 1000:
        #If we're approaching the ball and the opponent is close,
        #jump turn into ball to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = 0
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif abs(current_state.pos.y) < 350:
        #If we're close to the ball and the opponent is far away, take a single jump shot.
        controller_input.jump = 1

    elif current_state.wheel_contact:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        controller_input.boost = 1

    return controller_input
