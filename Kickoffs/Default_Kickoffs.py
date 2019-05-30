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


def offcenter(game_info, old_game_info, opponent_distance, x_sign):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(0, 0, 0)

    if current_state.pos.y < -3200:
        #Boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos+offset)).input()
        controller_input.boost = 1

    elif current_state.pos.y < - 2000 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1

    elif current_state.pos.z > 50:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.pos.y > -350:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and (current_state.vel.magnitude() > 2000):
        #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = -1
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif current_state.pos.y > -350:
        #If we're close and the opponent isn't, single jump to shoot on net
        controller_input.jump = 1
        controller_input.boost = 1

    else:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        controller_input.boost = 1


    return controller_input



#########################################################################################################

#########################################################################################################


def diagonal(game_info, old_game_info, opponent_distance, x_sign):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(0, 0, 0)

        
    if current_state.pos.y < -2400:
        #Boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos+offset)).input()
        controller_input.boost = 1

    elif current_state.pos.y < - 1500 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1

    elif current_state.pos.z > 50:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.pos.y > -350:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1,0,0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and (current_state.vel.magnitude() > 2000):
        #If we're approaching the ball and the opponent is close, jump turn to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = -1
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif current_state.pos.y > -350:
        #If we're close and the opponent isn't, single jump to shoot on net
        controller_input.jump = 1
        controller_input.boost = 1

    else:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        controller_input.boost = 1


    return controller_input
