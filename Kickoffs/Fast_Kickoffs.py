from math import atan2, sqrt, pi

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import Vec3
from Mechanics import AirDodge, CancelledFastDodge, JumpTurn, QuickTurn, FrontDodge, aerial_rotation
from Maneuvers import GroundTurn, FastDodge
from Miscellaneous import car_coordinates_2d
from GameState import Orientation


def far_back(game_info = None,
             opponent_distance = None,
             persistent = None):

    controller_input = SimpleControllerState()
    current_state = game_info.me
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


def offcenter(game_info = None,
              opponent_distance = None,
              x_sign = None,
              persistent = None):

    controller_input = SimpleControllerState()
    current_state = game_info.me
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
        if persistent.aerial_turn.action == None:
            persistent.aerial_turn.initialize = True

            vel_angle = atan2(current_state.vel.y, current_state.vel.x)
            target_rot = Orientation(pyr = [0, vel_angle, 0])
            persistent.aerial_turn.target_orientation = target_rot

        else:
            controller_input, persistent = aerial_rotation(game_info.dt,
                                                       persistent)
        controller_input.boost = 1


    return controller_input, persistent



#########################################################################################################

#########################################################################################################


def diagonal(game_info = None,
             x_sign = None,
             persistent = None):
    
    current_state = game_info.me
    controller_input = SimpleControllerState()
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(x_sign*game_info.team_sign*750,0,0)

    
    #Set which boost we want based on team and side.
    if game_info.team_sign == 1:
        if x_sign == -1:
            first_boost = 11
        else:
            first_boost = 10
    else:
        if x_sign == -1:
            first_boost = 22
        else:
            first_boost = 23
  
  
    if game_info.boosts[first_boost].is_active:
        #If we haven't taken the small boost yet, drive towards it
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = Vec3(0, -1000, 0))).input()
        controller_input.boost = 1
  
    elif abs(current_state.pos.y) > 1100 and current_state.wheel_contact:
        controller_input.jump = 1
        controller_input.boost = 1
  
    elif abs(current_state.pos.y) > 1100 and current_state.pos.z < 40:
        controller_input.jump = 1
        controller_input.boost = 1
  
    elif abs(current_state.pos.y) > 500 and not current_state.double_jumped:
        #If we've taken the boost but are still far away, fast dodge to speed up
        controller_input = CancelledFastDodge(current_state, Vec3(1, x_sign, 0)).input()
  
    elif abs(current_state.pos.y) > 250 and not current_state.wheel_contact:
        if persistent.aerial_turn.action == None:
            persistent.aerial_turn.initialize = True
            target_rot = Orientation(pitch = pi/3,
                                     yaw = current_state.rot.yaw,
                                     roll = 0)
            persistent.aerial_turn.target_orientation = target_rot
  
        else:
            controller_input, persistent = aerial_rotation(game_info.dt,
                                                                persistent)
        controller_input.boost = 1
        controller_input.steer = x_sign #Turn into the ball
  
    elif abs(current_state.pos.y) > 250:
        controller_input.throttle = 1
        controller_input.boost = 1
        controller_input.steer = x_sign
  
    else: 
        controller_input = FrontDodge(current_state).input()

    
    return controller_input, persistent














