from CowBotVector import * #This wasn't here before, but I'm not sure how it's not needed
from Mechanics import *
from Maneuvers import *
from GameState import * #Not needed?


def far_back(game_info, old_game_info, opponent_distance, persistent):
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
        dodge_direction = car_coordinates_2d(current_state, (game_info.ball.pos - Vec3(0,0,0)) - current_state.pos)
        controller_input = CancelledFastDodge(current_state, dodge_direction).input()

    elif abs(current_state.pos.y) < 400:# and opponent_distance < 1000:
        #Dodge into the ball.
        controller_input = AirDodge(Vec3(1, 0, 0),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact and abs(current_state.pos.y) < 1000:# and opponent_distance < 1000:
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

    return controller_input, persistent


#########################################################################################################

#########################################################################################################


def offcenter(game_info, old_game_info, opponent_distance, x_sign, persistent):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    #Offset added to the ball position for our initial steer
    offset = Vec3(x_sign*1200,0,0)

    first_boost = 7
    wobble = Vec3(current_state.omega.x, current_state.omega.y, 0).magnitude()
    epsilon = 0.01

    if abs(current_state.pos.y) > 3400:
        #If we're not near the center-line of the field, boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos+offset)).input()
        controller_input.boost = 1


    elif abs(current_state.pos.y) > 900 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 900 and not current_state.double_jumped:
        #If we're far away, fast dodge to speed up.
        dodge_direction = car_coordinates_2d(current_state, (game_info.ball.pos - Vec3(x_sign*2500,0,0)) - current_state.pos)
        controller_input = CancelledFastDodge(current_state, dodge_direction).input()
        controller_input.boost = 1

    elif abs(current_state.pos.y) < 250:
        #If both players are close to the ball, dodge into the ball.
        controller_input = AirDodge(Vec3(0,1,0),
                                    current_state.jumped_last_frame).input()
        controller_input.boost = 1

    elif current_state.wheel_contact and wobble < epsilon:
        #If we're approaching the ball and stable enough to jump again,
        #jump turn into ball to prep for the dodge
        if current_state.rot.yaw > ball_angle:
            direction = -1
        else:
            direction = 1
        controller_input = JumpTurn(current_state, 0, direction).input()

    elif current_state.wheel_contact:
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos)).input()
        controller_input.boost = 1

    else:
        vel_angle = atan2(current_state.vel.y, current_state.vel.x)
        target_rot = Orientation(pyr = [0, vel_angle, 0])
        controller_input, persistent = aerial_rotation(target_rot,
                                           game_info.dt,
                                           persistent)
        controller_input.boost = 1


    return controller_input, persistent



#########################################################################################################

#########################################################################################################


def diagonal(game_info, old_game_info,opponent_distance, x_sign, persistent):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    old_state = old_game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(x_sign*1500,-465,0)
    if current_state.rot.yaw > ball_angle:
        direction = -1
    else:
        direction = 1
    wobble = Vec3(current_state.omega.x, current_state.omega.y, 0).magnitude()
    epsilon = 0.3

    #Set which boost we want based on team and side.
    if x_sign == -1:
        first_boost = 11
    else:
        first_boost = 10

    if abs(current_state.pos.y) > 2440:
        #If we haven't taken the small boost yet, drive towards it
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = game_info.ball.pos + offset)).input()
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 1100 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1


    elif abs(current_state.pos.y) > 500:
        #If we've taken the boost but are still far away, fast dodge to speed up
        dodge_direction = car_coordinates_2d(current_state, (game_info.ball.pos - Vec3(x_sign*1000,0,0)) - current_state.pos)
        print(atan2(dodge_direction.y, dodge_direction.x))
        controller_input = CancelledFastDodge(current_state, dodge_direction).input()
        controller_input.steer = direction


    elif abs(current_state.pos.y) < 350:
        #If both players are close to the ball, dodge into the ball.
        controller_input = AirDodge(car_coordinates_2d(current_state,
                                                       game_info.ball.pos - current_state.pos),
                                    current_state.jumped_last_frame).input()

    elif current_state.wheel_contact:
        #If we're approaching the ball and the opponent is close,
        #jump turn into ball to prep for the dodge

        controller_input.steer = direction

    elif current_state.wheel_contact and abs(current_state.pos.y) < 520:
        controller_input.jump
    elif current_state.wheel_contact and wobble < epsilon:
        controller_input.handbrake = 1
    else:
        vel_angle = atan2(current_state.vel.y, current_state.vel.x)
        target_rot = Orientation(pyr = [0, vel_angle-x_sign*pi/4, 0])
        controller_input, persistent = aerial_rotation(target_rot,
                                           game_info.dt,
                                           persistent)
        controller_input.boost = 1
        controller_input.steer = x_sign

    return controller_input, persistent
