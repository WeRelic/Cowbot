from math import atan2

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import Vec3
from Maneuvers import GroundTurn
from Mechanics import FrontDodge


def far_back(game_info, opponent_distance):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)

    if abs(current_state.pos.y) > 3800:
        #If we're far away, boost to speed up
        controller_input.boost = 1

    elif abs(current_state.pos.y) > 1500:
        #Front flip for speed
        controller_input = FrontDodge(current_state).input()

    elif current_state.pos.y > -700:
        controller_input = FrontDodge(current_state).input()

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


def offcenter(game_info, opponent_distance, x_sign):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(0, 0, 0)

    if current_state.pos.y < -3200:
        #Boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos+offset)).input()
        controller_input.boost = 1

    elif current_state.pos.y < - 2000:
        controller_input = FrontDodge(current_state).input()

    elif current_state.pos.y > -700:
        controller_input = FrontDodge(current_state).input()

    else:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        if current_state.wheel_contact:
            controller_input.boost = 1


    return controller_input



#########################################################################################################

#########################################################################################################


def diagonal(game_info, opponent_distance, x_sign):
    controller_input = SimpleControllerState()
    current_state = game_info.me
    ball_angle = atan2((game_info.ball.pos - current_state.pos).y,
                       (game_info.ball.pos - current_state.pos).x)
    offset = Vec3(0, 0, 0)

        
    if current_state.pos.y < -2250:
        #Boost towards the first small boost
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos+offset)).input()
        controller_input.boost = 1

    elif current_state.pos.y < - 1500:
        controller_input = FrontDodge(current_state).input()

    elif current_state.pos.y > -700:
        controller_input = FrontDodge(current_state).input()

    else:
        #If we're on the ground between stages, boost and turn towards the ball
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos=game_info.ball.pos)).input()
        if current_state.wheel_contact:
            controller_input.boost = 1


    return controller_input
